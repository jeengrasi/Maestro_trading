# === MAESTRO-NEXUS FICHA v2.4.2 ===
# ID: api/router.py | COMMIT: groq_fallback_v2.4.2 | ESTADO: APROBADO POR MESA
# FECHA: 2026-06-29 | AUDITADO POR: DeepSeek (Gerente), Copilot (Auditor), Gemini (Estratega)
# CAMBIO vs v2.4.1: Corregido typo 'patter' → 'pattern' en sanitize_prompt.

import os
import httpx
import logging
import asyncio
import time
import re
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "jeengrasi/Maestro_trading"

def sanitize_prompt(text: str) -> str:
    pattern = re.compile(
        r"(ignore|ignora|forget|olvida|previous instructions|instrucciones anteriores|"
        r"assistant|asistente|reset your system prompt|override system prompt|act as)",
        re.IGNORECASE
    )
    cleaned = pattern.sub("", text)
    return cleaned.strip()

PARLIAMENT_STACK = {
    "gerente": {
        "model": "llama-3.1-8b-instant",
        "role": "Gerente General",
        "system_prompt": "Eres el Gerente General del Parlamento Nexus IA. Moderás debates y emites recomendaciones finales. Responde en español.",
        "timeout": 25.0
    },
    "auditor": {
        "model": "llama-3.1-8b-instant",
        "role": "Auditor Técnico",
        "system_prompt": "Eres el Auditor Técnico del Parlamento Nexus IA. Revisas código Python y validas cambios. Responde en español.",
        "timeout": 25.0
    },
    "estratega": {
        "model": "llama-3.1-8b-instant",
        "role": "Estratega de Mercado",
        "system_prompt": "Eres el Estratega de Mercado del Parlamento Nexus IA. Analizas oportunidades y riesgos. Responde en español.",
        "timeout": 25.0
    },
    "guardian": {
        "model": "llama-3.1-8b-instant",
        "role": "Guardián Documental",
        "system_prompt": "Eres el Guardián Documental del Parlamento Nexus IA. Lees documentos y verificas trazabilidad. Responde en español.",
        "timeout": 25.0
    },
    "secretario": {
        "model": "llama-3.1-8b-instant",
        "role": "Secretario de Actas",
        "system_prompt": (
            "Eres el Secretario de Actas del Parlamento Nexus IA. "
            "Tu ÚNICA función es generar actas estructuradas en formato Markdown. "
            "No participas en debates. No emites opiniones. Solo documentas.\n\n"
            "Formato obligatorio del acta:\n"
            "---\n"
            "ID: NEXUS-DEB-XXX\n"
            "Fecha: YYYY-MM-DD HH:MM\n"
            "Agentes: [lista de roles]\n"
            "Tema: [título del debate]\n"
            "Estado: Cerrado\n"
            "---\n"
            "# Acta del Debate\n\n"
            "## Contexto\n[breve descripción]\n\n"
            "## Posturas\n[resumen de cada IA]\n\n"
            "## Conclusión\n[decisión final]\n\n"
            "## Próximos Pasos\n[acciones acordadas]\n\n"
            "---\n"
            "**Pie de Página:** Acta generada por el Secretario de Actas del Parlamento Nexus IA."
        ),
        "timeout": 25.0
    }
}

async def call_ia(role: str, message: str) -> str:
    config = PARLIAMENT_STACK.get(role)
    if not config:
        return f"Error: Rol '{role}' no encontrado."
    
    message = sanitize_prompt(message)
    
    result = await call_groq(config, message)
    if not result.startswith("Error:"):
        return result
    
    logger.warning(f"Groq falló para {role}. Intentando OpenRouter...")
    result = await call_openrouter(config, message)
    if not result.startswith("Error:"):
        return result
    
    return f"Error: {config['role']} no disponible. Groq y OpenRouter fallaron."

async def call_groq(config: dict, message: str) -> str:
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY no configurada."
    
    start_time = time.perf_counter()
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": config["system_prompt"]},
            {"role": "user", "content": message}
        ]
    }
    for attempt in range(2):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(GROQ_URL, headers=headers, json=payload, timeout=config["timeout"])
                latency = time.perf_counter() - start_time
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Groq éxito: {config['role']} | Latencia: {latency:.2f}s")
                    return data["choices"][0]["message"]["content"]
                logger.warning(f"Groq intento {attempt+1}: {response.status_code}")
                await asyncio.sleep((attempt + 1) * 1)
        except Exception as e:
            logger.error(f"Groq excepción intento {attempt+1}: {e}")
            await asyncio.sleep(2)
    return "Error: Groq no disponible."

async def call_openrouter(config: dict, message: str) -> str:
    if not OPENROUTER_API_KEY:
        return "Error: OPENROUTER_API_KEY no configurada."
    
    start_time = time.perf_counter()
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openrouter/free",
        "messages": [
            {"role": "system", "content": config["system_prompt"]},
            {"role": "user", "content": message}
        ]
    }
    for attempt in range(2):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(OPENROUTER_URL, headers=headers, json=payload, timeout=45.0)
                latency = time.perf_counter() - start_time
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"OpenRouter éxito (fallback): {config['role']} | Latencia: {latency:.2f}s")
                    return data["choices"][0]["message"]["content"]
                logger.warning(f"OpenRouter intento {attempt+1}: {response.status_code}")
                await asyncio.sleep((attempt + 1) * 1)
        except Exception as e:
            logger.error(f"OpenRouter excepción intento {attempt+1}: {e}")
            await asyncio.sleep(2)
    return "Error: OpenRouter no disponible."

async def handle_parliament_debate(message: str) -> dict:
    results = {}
    roles_to_call = [r for r in PARLIAMENT_STACK.keys() if r not in ("gerente", "secretario")]
    tasks = [call_ia(role, message) for role in roles_to_call]
    responses = await asyncio.gather(*tasks)
    
    for role, response in zip(roles_to_call, responses):
        results[role] = {
            "role": PARLIAMENT_STACK[role]["role"],
            "model": PARLIAMENT_STACK[role]["model"],
            "response": response
        }
    return results

async def get_manager_recommendation(message: str, responses: dict) -> str:
    context = "Debate Parlamentario Nexus IA:\n\n"
    for role, data in responses.items():
        context += f"{data['role']}:\n{data['response']}\n\n"
    if len(context) > 8000:
        context = context[:8000] + "\n\n[Contexto truncado por longitud]"
    prompt = f"{context}\nComo Gerente General del Parlamento Nexus IA, basado en estas posturas, emite tu recomendación final."
    return await call_ia("gerente", prompt)

async def generate_acta(message: str, responses: dict, recommendation: str) -> str:
    debate_id = f"NEXUS-DEB-{datetime.now().strftime('%Y%m%d-%H%M')}"
    context = f"ID del debate: {debate_id}\n"
    context += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    context += f"Tema: {message}\n\n"
    context += "=== POSTURAS DE LAS IAs ===\n\n"
    
    for role, data in responses.items():
        context += f"--- {data['role']} ---\n{data['response']}\n\n"
    
    context += f"--- Gerente General (Recomendación Final) ---\n{recommendation}\n"
    context += "\nCon esta información, genera el acta del debate en formato Markdown siguiendo tu sistema de prompt."
    if len(context) > 8000:
        context = context[:8000] + "\n\n[Contexto truncado por longitud]"
    
    acta = await call_ia("secretario", context)
    return acta

async def save_acta_to_github(acta_content: str, debate_id: str) -> dict:
    if not GITHUB_TOKEN:
        logger.warning("GITHUB_TOKEN no configurada. Acta no guardada.")
        return {"status": "no_token"}
    
    filename = f"docs/actas/{debate_id}.md"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
    
    content_bytes = acta_content.encode("utf-8")
    content_base64 = base64.b64encode(content_bytes).decode("utf-8")
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json"
    }
    
    payload = {
        "message": f"Acta {debate_id} generada por Parlamento Nexus IA",
        "content": content_base64,
        "branch": "main"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=headers, json=payload, timeout=20.0)
            
            if response.status_code in (200, 201):
                logger.info(f"Acta guardada en GitHub: {filename}")
                return {"status": "success", "url": f"https://github.com/{GITHUB_REPO}/blob/main/{filename}"}
            else:
                logger.error(f"Error al guardar en GitHub: {response.status_code} - {response.text}")
                return {"status": "error", "code": response.status_code}
    except Exception as e:
        logger.error(f"Excepción al guardar en GitHub: {e}")
        return {"status": "error", "message": str(e)}
