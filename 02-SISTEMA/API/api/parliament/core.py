import re, os, httpx, logging, asyncio, time
logger = logging.getLogger(__name__)

# 4 PROVEEDORES INDEPENDIENTES PROBADOS
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
NVIDIA_NIM_API_KEY = os.getenv("NVIDIA_NIM_API_KEY")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")

MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
GITHUB_URL = "https://models.inference.ai.azure.com/chat/completions"
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
CLOUDFLARE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/meta/llama-3.1-8b-instruct" if CLOUDFLARE_ACCOUNT_ID else ""

def sanitize_prompt(text: str) -> str:
    pattern = re.compile(
        r"(ignore|ignora|forget|olvida|previous instructions|instrucciones anteriores|"
        r"assistant|asistente|reset your system prompt|override system prompt|act as)",
        re.IGNORECASE
    )
    return pattern.sub("", text).strip()

PARLIAMENT_STACK = {
    "gerente": {
        "model": "mistral-small", "role": "Gerente General", "provider": "mistral",
        "system_prompt": "Eres el Gerente General. REGLAS: Saludo: 1 línea. Ambiguo: pedir clarificación. Gobernanza: Contexto, Opciones, Decisión. Máximo 3 párrafos.",
        "timeout": 25.0
    },
    "auditor": {
        "model": "meta/llama-3.1-8b-instruct", "role": "Auditor", "provider": "nvidia",
        "system_prompt": "Eres el Auditor. En CUALQUIER debate, verifica: ¿Hay datos reales? ¿Hay fuentes? ¿Hay contradicciones? ¿Hay riesgos? Máximo 3 párrafos.",
        "timeout": 25.0
    },
    "estratega": {
        "model": "mistral-small", "role": "Estratega de Mercado", "provider": "mistral",
        "system_prompt": "Eres el Estratega de Mercado. Solo inversiones, trading, riesgo. Si no es mercado: 'No corresponde a Mercado'. Análisis → Riesgos → Recomendación. Máximo 4 párrafos.",
        "timeout": 25.0
    },
    "guardian": {
        "model": "gpt-4o-mini", "role": "Guardián Documental", "provider": "github",
        "system_prompt": "Eres el Guardián Documental. En CUALQUIER debate, verifica: ¿Hay actas previas? ¿Hay decisiones anteriores? ¿Está documentado? Máximo 2 párrafos.",
        "timeout": 25.0
    },
    "secretario": {
        "model": "@cf/meta/llama-3.1-8b-instruct", "role": "Secretario de Actas", "provider": "cloudflare",
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
                if r.status_code == 200: return r.json()["choices"][0]["message"]["content"]
                logger.warning(f"Mistral intento {attempt+1}: {r.status_code}")
                await asyncio.sleep(1)
        except Exception as e: logger.error(f"Mistral excepción: {e}"); await asyncio.sleep(1)
    return "Error: Mistral no disponible."

async def call_github(model: str, system_prompt: str, message: str, timeout: float) -> str:
    if not GITHUB_TOKEN: return "Error: GITHUB_TOKEN no configurada."
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}]}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(GITHUB_URL, headers=headers, json=payload, timeout=timeout)
            if r.status_code == 200: return r.json()["choices"][0]["message"]["content"]
            logger.warning(f"GitHub: {r.status_code}")
    except Exception as e: logger.error(f"GitHub excepción: {e}")
    return "Error: GitHub no disponible."

async def call_nvidia(model: str, system_prompt: str, message: str, timeout: float) -> str:
    if not NVIDIA_NIM_API_KEY: return "Error: NVIDIA_NIM_API_KEY no configurada."
    headers = {"Authorization": f"Bearer {NVIDIA_NIM_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}]}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(NVIDIA_URL, headers=headers, json=payload, timeout=timeout)
            if r.status_code == 200: return r.json()["choices"][0]["message"]["content"]
            logger.warning(f"NVIDIA: {r.status_code}")
    except Exception as e: logger.error(f"NVIDIA: {e}")
    return "Error: NVIDIA NIM no disponible."

async def call_cloudflare(model: str, system_prompt: str, message: str, timeout: float) -> str:
    if not CLOUDFLARE_API_TOKEN or not CLOUDFLARE_URL: return "Error: Cloudflare no configurado."
    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"}
    payload = {"messages": [{"role": "user", "content": f"{system_prompt}\n\n{message}"}]}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(CLOUDFLARE_URL, headers=headers, json=payload, timeout=timeout)
            if r.status_code == 200:
                data = r.json()
                return data.get("result", {}).get("response", data["result"]["choices"][0]["message"]["content"])
            logger.warning(f"Cloudflare: {r.status_code}")
    except Exception as e: logger.error(f"Cloudflare: {e}")
    return "Error: Cloudflare no disponible."

async def call_ia(role: str, message: str) -> str:
    config = PARLIAMENT_STACK.get(role)
    if not config: return f"Error: Rol '{role}' no encontrado."
    message = sanitize_prompt(message)
    provider = config.get("provider", "mistral")
    
    if provider == "mistral": result = await call_mistral(config["model"], config["system_prompt"], message, config["timeout"])
    elif provider == "github": result = await call_github(config["model"], config["system_prompt"], message, config["timeout"])
    elif provider == "nvidia": result = await call_nvidia(config["model"], config["system_prompt"], message, config["timeout"])
    elif provider == "cloudflare": result = await call_cloudflare(config["model"], config["system_prompt"], message, config["timeout"])
    else: return "Error: Proveedor no soportado."
    
    if not result.startswith("Error:"): return result
    logger.warning(f"{role} falló con {provider}. Intentando Mistral...")
    return await call_mistral("mistral-small", config["system_prompt"], message, config["timeout"])
