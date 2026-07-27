import os, httpx, logging, asyncio

logger = logging.getLogger(__name__)
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

async def call_mistral(model: str, system_prompt: str, message: str, timeout: float = 30.0) -> str:
    if not MISTRAL_API_KEY:
        return "Error: MISTRAL_API_KEY no configurada en Vercel."
    
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(MISTRAL_URL, headers=headers, json=payload, timeout=timeout)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            logger.error(f"Error Mistral: {response.status_code} - {response.text}")
            return f"Error: Mistral respondió con código {response.status_code}"
    except Exception as e:
        logger.error(f"Excepción en Mistral: {e}")
        return f"Error de conexión con Mistral: {str(e)}"
