from fastapi import APIRouter
import httpx
import os
import time

router = APIRouter()

@router.get("/health")
async def health():
    start = time.time()

    # 1. Verificar Upstash con PING (solo lectura)
    upstash_url = os.getenv("UPSTASH_REDIS_REST_URL")
    upstash_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.post(
                upstash_url,
                headers={"Authorization": f"Bearer {upstash_token}"},
                json={"command": ["PING"]}
            )
        redis_ok = (r.status_code == 200 and r.json().get("result") == "PONG")
    except Exception:
        redis_ok = False

    # 2. Tiempo de respuesta
    latency = round((time.time() - start) * 1000, 2)

    # 3. Respuesta JSON
    return {
        "status": "ok" if redis_ok else "degraded",
        "redis": redis_ok,
        "latency_ms": latency
    }

