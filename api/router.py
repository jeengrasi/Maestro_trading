# === MAESTRO-NEXUS FICHA v2.0.1 ===
# ID: api/router.py | COMMIT: huggingface_v2.0.1 | ESTADO: PRODUCCIÓN
# FECHA: 2026-06-28 | AUDITADO POR: DeepSeek (Gerente), Gemini (Estratega), Copilot (Auditor)
# CAMBIO vs v2.0: Guardián reemplazado por Zephyr-7B (ligero, compatible con HuggingFace Free Tier).

import os
import httpx
import logging
import asyncio
import time
import re

logger = logging.getLogger(__name__)

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_URL = "https://api-inference.huggingface.co/models"

if not HUGGINGFACE_API_KEY:
    logger.error("CRÍTICO: HUGGINGFACE_API_KEY no configurada en Vercel.")
    raise RuntimeError("Sistema detenido: Falta clave de API de HuggingFace.")

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
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "role": "Gerente General",
        "system_prompt": "Eres el Gerente General del Parlamento Nexus IA. Moderás debates y emites recomendaciones finales. Responde en español.",
        "timeout": 45.0
    },
    "auditor": {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "role": "Auditor Técnico",
        "system_prompt": "Eres el Auditor Técnico del Parlamento Nexus IA. Revisas código Python y validas cambios. Responde en español.",
        "timeout": 30.0
    },
    "estratega": {
        "model": "google/gemma-2-9b-it",
        "role": "Estratega de Mercado",
        "system_prompt": "Eres el Estratega de Mercado del Parlamento Nexus IA. Analizas oportunidades y riesgos. Responde en español.",
        "timeout": 30.0
    },
    "guardian": {
        "model": "HuggingFaceH4/zephyr-7b-beta",
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
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": f"{config['system_prompt']}\n\nUsuario: {message}\n\nAsistente:",
        "parameters": {
            "max_new_tokens": 500,
            "return_full_text": False
        }
    }
    
    for attempt in range(2):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{HUGGINGFACE_URL}/{config['model']}",
                    headers=headers,
                    json=payload,
                    timeout=config["timeout"]
                )
                
                latency = time.perf_counter() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Éxito: {role} | Modelo: {config['model']} | Latencia: {latency:.2f}s")
                    if isinstance(data, list) and len(data) > 0:
                        return data[0].get("generated_text", "Error: Respuesta vacía.")
                    return "Error: Respuesta inesperada de HuggingFace."
                
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
