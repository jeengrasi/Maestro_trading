import os, httpx, logging, asyncio, time
logger = logging.getLogger(__name__)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

async def call_groq(model: str, system_prompt: str, message: str, timeout: float = 25.0) -> str:
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY no configurada."
    start_time = time.perf_counter()
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}]}
    for attempt in range(2):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(GROQ_URL, headers=headers, json=payload, timeout=timeout)
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Groq | Latencia: {time.perf_counter() - start_time:.2f}s")
                    return data["choices"][0]["message"]["content"]
                logger.warning(f"Groq intento {attempt+1}: {response.status_code}")
                await asyncio.sleep((attempt + 1) * 1)
        except Exception as e:
            logger.error(f"Groq excepción: {e}")
            await asyncio.sleep(2)
    return "Error: Groq no disponible."
