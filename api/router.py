# === MAESTRO-NEXUS FICHA v1.4 ===
# ID: api/router.py | COMMIT: free_models_v1.4 | ESTADO: CORREGIDO
# GERENTE: DeepSeek. Stack 100% gratuito con modelos verificados en OpenRouter.
# CAMBIO: Solo se reemplazaron los nombres de modelos. El resto del código es idéntico a v1.3.

import os
import httpx
import logging
import asyncio

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_API_KEY:
    logger.error("OPENROUTER_API_KEY no está configurada en Vercel.")
    raise RuntimeError("OPENROUTER_API_KEY no configurada. El Parlamento no puede iniciar.")

# === SANITIZACIÓN DE PROMPTS ===
def sanitize_prompt(text: str) -> str:
    """Limpia el mensaje de instrucciones peligrosas o loops."""
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

# === STACK PARLAMENTARIO (MODELOS 100% GRATUITOS VERIFICADOS) ===
PARLIAMENT_STACK = {
    "gerente": {
        "model": "nvidia/nemotron-3-super",
        "role": "Gerente General",
        "system_prompt": (
            "Eres el Gerente General del Parlamento Nexus IA, un sistema autónomo de trading. "
            "Tu función es moderar debates, analizar las posturas de las IAs especialistas "
            "y emitir una recomendación final clara y concisa. "
            "Responde siempre en español."
        ),
        "timeout": 30.0
    },
    "auditor": {
        "model": "google/gemma-4-31b",
        "role": "Auditor Técnico",
        "system_prompt": (
            "Eres el Auditor Técnico del Parlamento Nexus IA. "
            "Tu función es revisar código Python, detectar errores, validar cambios "
            "y asegurar que las propuestas cumplen con la Constitución Nexus. "
            "Responde siempre en español."
        ),
        "timeout": 25.0
    },
    "estratega": {
        "model": "google/gemma-4-26b-a4b",
        "role": "Estratega de Mercado",
        "system_prompt": (
            "Eres el Estratega de Mercado del Parlamento Nexus IA. "
            "Tu función es analizar oportunidades de inversión, evaluar riesgos macroeconómicos "
            "y recomendar acciones basadas en datos. "
            "Responde siempre en español."
        ),
        "timeout": 25.0
    },
    "guardian": {
        "model": "cohere/north-mini-code",
        "role": "Guardián Documental",
        "system_prompt": (
            "Eres el Guardián Documental del Parlamento Nexus IA. "
            "Tu función es leer documentos del proyecto, verificar trazabilidad, "
            "citar fuentes y proveer memoria institucional. "
            "Responde siempre en español."
        ),
        "timeout": 25.0
    }
}

async def call_ia(role: str, message: str) -> str:
    """Llama a una IA del Parlamento a través de OpenRouter."""
    
    config = PARLIAMENT_STACK.get(role)
    if not config:
        return f"Error: Rol '{role}' no encontrado en el Parlamento."
    
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
                else:
                    logger.error(f"Respuesta inesperada de {config['model']}: {data}")
                    return f"Error: Respuesta inesperada de {config['role']}."
            elif response.status_code == 402:
                return f"Error: Sin créditos en OpenRouter."
            else:
                logger.error(f"Error {config['model']}: {response.status_code} - {response.text}")
                return f"Error: {config['role']} no está disponible. Código: {response.status_code}"
    except httpx.TimeoutException:
        logger.error(f"Timeout al llamar a {config['model']}")
        return f"Error: {config['role']} tardó demasiado en responder."
    except Exception as e:
        logger.error(f"Excepción al llamar a {config['role']}: {e}")
        return f"Error: No se pudo contactar a {config['role']}."

async def handle_parliament_debate(message: str) -> dict:
    """Ejecuta un debate completo entre todas las IAs del Parlamento en PARALELO."""
    
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
    """Obtiene la recomendación final del Gerente basada en las respuestas de todas las IAs."""
    
    context = "Debate Parlamentario Nexus IA:\n\n"
    for role, data in responses.items():
        context += f"{data['role']} ({data['model']}):\n{data['response']}\n\n"
    
    prompt = f"{context}\nComo Gerente General del Parlamento Nexus IA, basado en estas posturas, emite tu recomendación final y conclusión."
    
    return await call_ia("gerente", prompt)
