# === MAESTRO-NEXUS FICHA v2.1 ===
# ID: api/router.py | COMMIT: openrouter_free_v2.1 | ESTADO: PRODUCCIÓN
# FECHA: 2026-06-28 | AUDITADO POR: DeepSeek (Gerente)
# CAMBIO vs v2.0.1: HuggingFace → OpenRouter con modelo gratuito openrouter/free.
# MOTIVO: HuggingFace Inference API no resuelve DNS consistentemente.

import os
import httpx
import logging
import asyncio
import time
import re

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_API_KEY:
    logger.error("CRÍTICO: OPENROUTER_API_KEY no configurada en Vercel.")
    raise RuntimeError("Sistema detenido: Falta clave de API de OpenRouter.")

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
        "model": "openrouter/free",
        "role": "Gerente General",
        "system_prompt": "Eres el Gerente General del Parlamento Nexus IA. Moderás debates y emites recomendaciones finales. Responde en español.",
        "timeout": 45.0
    },
    "auditor": {
        "model": "openrouter/free",
        "role": "Auditor Técnico",
        "system_prompt": "Eres el Auditor Técnico del Parlamento Nexus IA. Revisas código Python y validas cambios. Responde en español.",
        "timeout": 30.0
    },
    "estratega": {
        "model": "openrouter/free",
        "role": "Estratega de Mercado",
        "system_prompt": "Eres el Estratega de Mercado del Parlamento Nexus IA. Analizas oportunidades y riesgos. Responde en español.",
        "timeout": 30.0
    },
    "guardian": {
        "model": "openrouter/free",
        "role": "Guardián Documental",
        "system_prompt": "Eres el Guardián Documental del Parlamento Nexus IA. Lees documentos y verificas trazabilidad. Responde en español.",
        "timeout": 40.0
    }
}

async def call_ia(role: str, message: str) -> str:
    config = PARLIAMENT_STACK.get(role)
    if not config:
        return f"Error: Rol '{role}' no encontrado."
    
    message = sanitize_prompt(message)
    start_time = time.perf_counter()
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
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
                response = await client.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json=payload,
                    timeout=config["timeout"]
                )
                
                latency = time.perf_counter() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Éxito: {role} | Latencia: {latency:.2f}s")
                    return data["choices"][0]["message"]["content"]
                
                logger.warning(f"Intento {attempt+1} fallido para {role}: {response.status_code}")
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error {role} (intento {attempt+1}): {e}")
            await asyncio.sleep(1)
            
    return f"Error: {config['role']} no disponible tras intentos."

async def handle_parliament_debate(message: str) -> dict:
    results = {}
    roles_to_call = [r for r in PARLIAMENT_STACK.keys() if r != "gerente"]
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
        context += f"{data['role']} ({data['model']}):\n{data['response']}\n\n"
    
    prompt = f"{context}\nComo Gerente General del Parlamento Nexus IA, basado en estas posturas, emite tu recomendación final."
    return await call_ia("gerente", prompt)
