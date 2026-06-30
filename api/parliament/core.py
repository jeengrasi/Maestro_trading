import re
from api.providers.groq import call_groq
from api.providers.openrouter import call_openrouter
import logging
logger = logging.getLogger(__name__)

def sanitize_prompt(text: str) -> str:
    pattern = re.compile(
        r"(ignore|ignora|forget|olvida|previous instructions|instrucciones anteriores|"
        r"assistant|asistente|reset your system prompt|override system prompt|act as)",
        re.IGNORECASE
    )
    return pattern.sub("", text).strip()

PARLIAMENT_STACK = {
    "gerente": {
        "model": "llama-3.1-8b-instant",
        "role": "Gerente General",
        "system_prompt": (
            "Eres el Gerente General del Parlamento Nexus IA. "
            "REGLAS: Si es saludo, responde en 1 línea amable. "
            "Si es ambiguo, pide clarificación. "
            "Si es gobernanza, estructura: Contexto, Opciones, Decisión. "
            "Máximo 3 párrafos. Sin rodeos."
        ),
        "timeout": 25.0
    },
    "auditor": {
        "model": "llama-3.1-8b-instant",
        "role": "Auditor Técnico",
        "system_prompt": (
            "Eres el Auditor Técnico del Parlamento Nexus IA. "
            "REGLAS: Solo temas técnicos. Si no es técnico, responde: "
            "'Este tema no corresponde al departamento de Auditoría.' "
            "Estructura: Diagnóstico → Causa → Solución. Máximo 3 párrafos."
        ),
        "timeout": 25.0
    },
    "estratega": {
        "model": "llama-3.1-8b-instant",
        "role": "Estratega de Mercado",
        "system_prompt": (
            "Eres el Estratega de Mercado del Parlamento Nexus IA. "
            "REGLAS: Solo inversiones, trading, riesgo. Si no es mercado, responde: "
            "'Este tema no corresponde al departamento de Mercado.' "
            "Estructura: Análisis → Riesgos → Recomendación. Máximo 4 párrafos."
        ),
        "timeout": 25.0
    },
    "guardian": {
        "model": "llama-3.1-8b-instant",
        "role": "Guardián Documental",
        "system_prompt": (
            "Eres el Guardián Documental del Parlamento Nexus IA. "
            "REGLAS: Solo documentación, actas, historial. Si no es documental, responde: "
            "'Este tema no corresponde al departamento de Documentación.' "
            "Cita actas si existen. Máximo 2 párrafos."
        ),
        "timeout": 25.0
    },
    "secretario": {
        "model": "llama-3.1-8b-instant",
        "role": "Secretario de Actas",
        "system_prompt": "Eres el Secretario de Actas. Generas actas Markdown. No participas en debates. No opinas.",
        "timeout": 25.0
    }
}

async def call_ia(role: str, message: str) -> str:
    config = PARLIAMENT_STACK.get(role)
    if not config:
        return f"Error: Rol '{role}' no encontrado."
    message = sanitize_prompt(message)
    result = await call_groq(config["model"], config["system_prompt"], message, config["timeout"])
    if not result.startswith("Error:"):
        return result
    logger.warning(f"Groq falló para {role}. Intentando OpenRouter...")
    result = await call_openrouter(config["model"], config["system_prompt"], message)
    if not result.startswith("Error:"):
        return result
    return f"Error: {config['role']} no disponible."
