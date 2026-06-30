# === MAESTRO-NEXUS: PROVEEDOR OPENROUTER ===
# ID: api/providers/openrouter.py | ESTADO: MODULARIZADO
# FECHA: 2026-06-30 | Extraído de api/router.py v2.4.2

import os
import httpx
import logging
import asyncio
import time

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

async def call_openrouter(model: str, system_prompt: str, message: str, timeout: float = 45.0) -> str:
    if not OPENROUTER_API_KEY:
        return "Error: OPENROUTER_API_KEY no configurada."
    
    start_time = time.perf_counter()
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openrouter/free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    }
    for attempt in range(2):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(OPENROUTER_URL, headers=headers, json=payload, timeout=timeout)
                latency = time.perf_counter() - start_time
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"OpenRouter (fallback) | Latencia: {latency:.2f}s")
                    return data["choices"][0]["message"]["content"]
                logger.warning(f"OpenRouter intento {attempt+1}: {response.status_code}")
                await asyncio.sleep((attempt + 1) * 1)
        except Exception as e:
            logger.error(f"OpenRouter excepción intento {attempt+1}: {e}")
            await asyncio.sleep(2)
    return "Error: OpenRouter no disponible."
