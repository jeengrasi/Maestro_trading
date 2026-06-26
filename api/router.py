}}# === MAESTRO-NEXUS FICHA v1.7 ===
# ID: api/router.py | COMMIT: verified_free_v1.7 | ESTADO: CORREGIDO
# GERENTE: DeepSeek. Modelos verificados en OpenRouter al 26-jun-2026.

import os
import httpx
import logging
import asyncio

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_API_KEY:
    logger.error("OPENROUTER_API_KEY no configurada.")
    raise RuntimeError("OPENROUTER_API_KEY no configurada.")

def sanitize_prompt(text: str) -> str:
    forbidden = [
        "ignora las instrucciones anteriores",
        "ignore previous instructions",
        "eres un asistente",
        "you are an assistant"
    ]
    cleaned = text
    for phrase in forbidden:
        cleaned = cleaned.replace(phrase, "")
    return cleaned.strip()

PARLIAMENT_STACK = {
    "gerente": {
        "model": "qwen/qwen3-next-80b-a3b-instruct",
        "role": "Gerente General",
        "system_prompt": "Eres el Gerente General del Parlamento Nexus IA. Moderás debates y emites recomendaciones finales. Responde en español.",
        "timeout": 30.0
    },
    "auditor": {
        "model": "meta-llama/llama-3.3-70b-instruct",
        "role": "Auditor Técnico",
        "system_prompt": "Eres el Auditor Técnico del Parlamento Nexus IA. Revisas código Python y validas cambios. Responde en español.",
        "timeout": 25.0
    },
    "estratega": {
        "model": "google/gemma-4-26b-a4b",
        "role": "Estratega de Mercado",
        "system_prompt": "Eres el Estratega de Mercado del Parlamento Nexus IA. Analizas oportunidades y riesgos. Responde en español.",
        "timeout": 25.0
    },
    "guardian": {
        "model": "nvidia/nemotron-3.5-content-safety",
        "role": "Guardián Documental",
        "system_prompt": "Eres el Guardián Documental del Parlamento Nexus IA. Lees documentos y verificas trazabilidad. Responde en español.",
        "timeout": 30.0
    }
}

async def call_ia(role: str, message: str) -> str:
    config = PARLIAMENT_STACK.get(role)
    if not config:
        return f"Error: Rol '{role}' no encontrado."
    
    message = sanitize_prompt(message)
    
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
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=config["timeout"]
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                return "Error: Respuesta vacía."
            elif response.status_code == 402:
                return "Error: Sin créditos en OpenRouter."
            else:
                logger.error(f"Error {config['model']}: {response.status_code}")
                return f"Error: {config['role']} no disponible. Código: {response.status_code}"
    except httpx.TimeoutException:
        return f"Error: {config['role']} tardó demasiado."
    except Exception as e:
        return f"Error: No se pudo contactar a {config['role']}."

async def handle_parliament_debate(message: str) -> dict:
    results = {}
    roles_to_call = [r for r in PARLIAMENT_STACK.keys() if r != "gerente"]
    tasks = [call_ia(role, message) for role in roles_to_call]
    responses = await asyncio.gather(*tasks)
    
    for role, response in zip(roles_to_call, responses):
        config = PARLIAMENT_STACK[role]
        results[role] = {
            "role": config["role"],
            "model": config["model"],
            "response": response
        }
    
    return results

async def get_manager_recommendation(message: str, responses: dict) -> str:
    context = "Debate Parlamentario Nexus IA:\n\n"
    for role, data in responses.items():
        context += f"{data['role']} ({data['model']}):\n{data['response']}\n\n"
    
    prompt = f"{context}\nComo Gerente General, basado en estas posturas, emite tu recomendación final."
    
    return await call_ia("gerente", prompt)
