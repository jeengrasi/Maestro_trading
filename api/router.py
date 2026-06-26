# === MAESTRO-NEXUS FICHA v1.5 ===
# ID: api/router.py | COMMIT: verified_models_v1.5 | ESTADO: CORREGIDO POR MESA
# GERENTE: DeepSeek. Stack verificado con modelos reales de OpenRouter.
# CORRECCIÓN: Nombres de modelos validados por Copilot y Gemini.

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

# === STACK PARLAMENTARIO (MODELOS VERIFICADOS EN OPENROUTER) ===
PARLIAMENT_STACK = {
    "gerente": {
        "model": "google/gemini-2.0-flash-thinking-exp",
        "role": "Gerente General",
        "system_prompt": (
            "Eres el Gerente General del Parlamento Nexus IA. "
            "Moderas debates, analizas posturas de IAs especialistas "
            "y emites una recomendación final clara y concisa. "
            "Responde siempre en español."
        ),
        "timeout": 40.0
    },
    "auditor": {
        "model": "deepseek/deepseek-r1",
        "role": "Auditor Técnico",
        "system_prompt": (
            "Eres el Auditor Técnico del Parlamento Nexus IA. "
            "Revisas código Python, detectas errores, validas cambios "
            "y aseguras el cumplimiento de la Constitución Nexus. "
            "Responde siempre en español."
        ),
        "timeout": 30.0
    },
    "estratega": {
        "model": "qwen/qwen-2.5-72b-instruct",
        "role": "Estratega de Mercado",
        "system_prompt": (
            "Eres el Estratega de Mercado del Parlamento Nexus IA. "
            "Analizas oportunidades de inversión, evalúas riesgos macroeconómicos "
            "y recomiendas acciones basadas en datos. "
            "Responde siempre en español."
        ),
        "timeout": 30.0
    },
    "guardian": {
        "model": "meta-llama/llama-3.3-70b-instruct",
        "role": "Guardián Documental",
        "system_prompt": (
            "Eres el Guardián Documental del Parlamento Nexus IA. "
            "Lees documentos del proyecto, verificas trazabilidad, "
            "citas fuentes y provees memoria institucional. "
            "Responde siempre en español."
        ),
        "timeout": 30.0
    }
}

async def call_ia(role: str, message: str) -> str:
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
        ],
        "provider": {
            "order": ["Groq", "Together", "DeepInfra", "OpenRouter"],
            "allow_fallbacks": True
        }
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
                return f"Error: {config['role']} no disponible. Código: {response.status_code}"
    except httpx.TimeoutException:
        logger.error(f"Timeout al llamar a {config['model']}")
        return f"Error: {config['role']} tardó demasiado."
    except Exception as e:
        logger.error(f"Excepción al llamar a {config['role']}: {e}")
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
