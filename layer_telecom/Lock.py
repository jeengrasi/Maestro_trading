# === MAESTRO-NEXUS FICHA v1.1 ===
# ID: layer_telecom/lock.py | COMMIT: lock_v1.5_chatops | ESTADO: MODIFICABLE
# COVERAGE: 97% | COST_UPSTASH: 5 ops/call | RIESGO: BAJO
# ÚLTIMO_TEST: 2026-05-24 PASS | DIRECTOR_ID: JEISSON_01
# CTO: Lock NX + FIFO + Speaker timeout 30s. Deriva bloques de código a la Capa 3.
# AUDITOR: Corregido por Meta. Inyecta el disparador asíncrono hacia process_staging_request.

import os
import httpx
from datetime import datetime

# [LÍNEA 1] Función principal: recibe el mensaje de Telegram y la instancia de base de datos
async def handle_m2m_message(payload: dict, redis):
    msg_id = payload.get("message", {}).get("message_id")
    sender = payload.get("message", {}).get("from", {}).get("username", "unknown")
    text = payload.get("message", {}).get("text", "")
    
    # [LÍNEA 2] IDEMPOTENCIA: Bloquea mensajes repetidos o reintentos de la API de Telegram
    if not await redis.set(f"processed:{msg_id}", "1", nx=True, ex=3600):
        return {"status": "duplicate_ignored"}
        
    # [LÍNEA 3] LOCK ATÓMICO: Evita colisiones de escritura en el servidor serverless
    if not await redis.set("parliament:lock", "1", nx=True, ex=5):
        await redis.lpush("parliament:queue", f"{msg_id}:{sender}:{text}")
        return {"status": "enqueued_in_fifo"}
        
    try:
        # [LÍNEA 4.1] SPEAKER TIMEOUT: Otorga turno de habla por 30 segundos para evitar congelamientos
        await redis.set("parliament:current_speaker", sender, ex=30)
        await redis.set("parliament:debate_status", "IN_DEBATE")
        await redis.lpush(f"parliament:history:{datetime.now().strftime('%Y-%m-%d')}", text)
        
        # [LÍNEA 4.2] DISPARADOR CAPA 3: Si el mensaje contiene código o un commit, activa la Fábrica
        if "```python" in text or "COMMIT:" in text:
            from layer_chatops.staging import process_staging_request
            return await process_staging_request(text, msg_id, sender, redis)
        
        # [LÍNEA 4.3] Si el texto es una charla normal en prosa, el flujo continúa de forma natural
        return {"status": "processed", "speaker": sender}
        
    finally:
        # [LÍNEA 5] LIBERACIÓN: Quita el candado y procesa el siguiente mensaje en la fila de espera
        await redis.delete("parliament:lock")
        next_item = await redis.rpop("parliament:queue")
        if next_item:
            vercel_url = os.getenv("VERCEL_URL")
            async with httpx.AsyncClient() as client:
                await client.post(f"{vercel_url}/webhook", json={"replay": next_item})
