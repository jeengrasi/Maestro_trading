import re, os, httpx, logging, asyncio, time
logger = logging.getLogger(__name__)

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
GOOGLE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
GITHUB_URL = "https://models.inference.ai.azure.com/chat/completions"

def sanitize_prompt(text: str) -> str:
    pattern = re.compile(
        r"(ignore|ignora|forget|olvida|previous instructions|instrucciones anteriores|"
        r"assistant|asistente|reset your system prompt|override system prompt|act as)",
        re.IGNORECASE
    )
    return pattern.sub("", text).strip()

PARLIAMENT_STACK = {
    "gerente": {
        "model": "mistral-small", "role": "Gerente General",
        "system_prompt": "Eres el Gerente General. REGLAS: Saludo: 1 línea. Ambiguo: pedir clarificación. Gobernanza: Contexto, Opciones, Decisión. Máximo 3 párrafos.",
        "timeout": 25.0
    },
    "auditor": {
        "model": "mistral-small", "role": "Auditor Técnico",
        "system_prompt": "Eres el Auditor Técnico. REGLAS: Solo temas técnicos. Si no es técnico: 'No corresponde a Auditoría'. Diagnóstico → Causa → Solución. Máximo 3 párrafos.",
        "timeout": 25.0
    },
    "estratega": {
        "model": "mistral-small", "role": "Estratega de Mercado",
        "system_prompt": "Eres el Estratega de Mercado. REGLAS: Solo inversiones, trading, riesgo. Si no es mercado: 'No corresponde a Mercado'. Análisis → Riesgos → Recomendación. Máximo 4 párrafos.",
        "timeout": 25.0
    },
    "guardian": {
        "model": "mistral-small", "role": "Guardián Documental",
        "system_prompt": "Eres el Guardián Documental. REGLAS: Solo documentación, actas, historial. Si no es documental: 'No corresponde a Documentación'. Cita actas si existen. Máximo 2 párrafos.",
        "timeout": 25.0
    },
    "secretario": {
        "model": "mistral-small", "role": "Secretario de Actas",
        "system_prompt": "Eres el Secretario de Actas. Generas actas Markdown. No participas en debates. No opinas.",
        "timeout": 25.0
    }
}

async def call_mistral(model: str, system_prompt: str, message: str, timeout: float) -> str:
    if not MISTRAL_API_KEY: return "Error: MISTRAL_API_KEY no configurada."
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}]}
    for attempt in range(2):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(MISTRAL_URL, headers=headers, json=payload, timeout=timeout)
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
                logger.warning(f"Mistral intento {attempt+1}: {r.status_code}")
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Mistral excepción: {e}")
            await asyncio.sleep(1)
    return "Error: Mistral no disponible."

async def call_google(model: str, system_prompt: str, message: str, timeout: float) -> str:
    if not GOOGLE_API_KEY: return "Error: GOOGLE_API_KEY no configurada."
    headers = {"Authorization": f"Bearer {GOOGLE_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "gemini-2.0-flash", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}]}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(GOOGLE_URL, headers=headers, json=payload, timeout=timeout)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            logger.warning(f"Google: {r.status_code}")
            if r.status_code == 429:
                await asyncio.sleep(20)
                return await call_google(model, system_prompt, message, timeout)
    except Exception as e:
        logger.error(f"Google excepción: {e}")
    return "Error: Google no disponible."

async def call_github(model: str, system_prompt: str, message: str, timeout: float) -> str:
    if not GITHUB_TOKEN: return "Error: GITHUB_TOKEN no configurada."
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Content-Type": "application/json"}
    payload = {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}]}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(GITHUB_URL, headers=headers, json=payload, timeout=timeout)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            logger.warning(f"GitHub: {r.status_code}")
    except Exception as e:
        logger.error(f"GitHub excepción: {e}")
    return "Error: GitHub no disponible."

async def call_ia(role: str, message: str) -> str:
    config = PARLIAMENT_STACK.get(role)
    if not config:
        return f"Error: Rol '{role}' no encontrado."
    message = sanitize_prompt(message)
    
    # Cascada: Mistral → Google → GitHub
    result = await call_mistral(config["model"], config["system_prompt"], message, config["timeout"])
    if not result.startswith("Error:"): return result
    
    logger.warning(f"Mistral falló para {role}. Intentando Google...")
    result = await call_google(config["model"], config["system_prompt"], message, config["timeout"])
    if not result.startswith("Error:"): return result
    
    logger.warning(f"Google falló para {role}. Intentando GitHub...")
    result = await call_github(config["model"], config["system_prompt"], message, config["timeout"])
    if not result.startswith("Error:"): return result
    
    return f"Error: {config['role']} no disponible. Mistral, Google y GitHub fallaron."
