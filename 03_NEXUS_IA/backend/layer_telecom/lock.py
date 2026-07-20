# === MAESTRO-NEXUS FICHA v1.7 ===
# ID: layer_telecom/lock.py | COMMIT: fix_sync_redis_v1.7 | ESTADO: CORREGIDO
# FECHA: 2026-06-28 | AUDITADO POR: DeepSeek (Gerente)
# CAMBIO: Eliminados TODOS los await de llamadas a Redis (Upstash es síncrono).
# Este error bloqueaba el flujo parlamentario antes de llegar al router.py.

import os
import httpx
from datetime import datetime

async def handle_m2m_message(payload: dict, redis):

    # --- Anti-loop: metadatos de replay ---
    replay_meta = payload.get("replay_meta", {}) or {}
    is_replay = bool(replay_meta.get("is_replay"))
    replay_count = int(replay_meta.get("count", 0))

    if is_replay and replay_count > 3:
        return {"status": "critical_loop_prevented_drop"}

    message = payload.get("message", {}) or {}
    msg_id = message.get("message_id")
    sender = (message.get("from") or {}).get("username", "unknown")
    text = message.get("text", "") or ""

    # --- Enmienda 1: Guard para msg_id None ---
    if msg_id is None:
        return {"status": "missing_msg_id"}

    # --- Idempotencia: TTL 120s ---
    # CORREGIDO: Eliminado await. Redis de Upstash es síncrono.
    processed_key = f"processed:{msg_id}"
    if not redis.set(processed_key, "1", nx=True, ex=120):
        return {"status": "duplicate_ignored"}

    # --- Lock atómico 15s ---
    # CORREGIDO: Eliminado await.
    if not redis.set("parliament:lock", "1", nx=True, ex=15):
        redis.lpush("parliament:queue", f"{msg_id}:{sender}:{text}")
        return {"status": "enqueued_in_fifo"}

    try:
        # Estado del Parlamento
        # CORREGIDO: Eliminado await.
        redis.set("parliament:current_speaker", sender, ex=30)
        redis.set("parliament:debate_status", "IN_DEBATE")

        # Historial acotado
        today = datetime.now().strftime("%Y-%m-%d")
        history_key = f"parliament:history:{today}"
        redis.lpush(history_key, text)
        redis.ltrim(history_key, 0, 999)

        # Circuit breaker Capa 3
        circuit_key = "circuit_breaker:staging"
        # CORREGIDO: Eliminado await.
        circuit_failures = redis.get(circuit_key)
        try:
            circuit_failures = int(circuit_failures) if circuit_failures else 0
        except:
            circuit_failures = 0

        # Disparador Capa 3
        if ("```python" in text or "COMMIT:" in text) and len(text) > 50 and circuit_failures <= 5:
            from layer_chatops.staging import process_staging_request
            try:
                return await process_staging_request(text, msg_id, sender, redis)
            except Exception as e:
                # CORREGIDO: Eliminado await.
                redis.incr(circuit_key)
                redis.expire(circuit_key, 300)
                return {"status": "staging_error_circuit_incremented", "error": str(e)}

        return {"status": "processed", "speaker": sender}

    finally:
        # --- Replay FIFO antes de liberar lock ---
        # CORREGIDO: Eliminado await.
        next_item = redis.rpop("parliament:queue")
        redis.delete("parliament:lock")

        if next_item:
            raw_url = os.getenv("VERCEL_URL", "").strip()
            if not raw_url:
                return {"status": "missing_vercel_url_no_replay"}

            vercel_url = raw_url if raw_url.startswith("https://") else f"https://{raw_url}"

            # --- Enmienda 2: Reconstrucción correcta del mensaje en cola ---
            try:
                parts = next_item.split(":", 2)
                v_msg_id = int(parts[0]) if parts[0] != "None" else None
                v_sender = parts[1]
                v_text = parts[2]
            except:
                v_msg_id = msg_id
                v_sender = sender
                v_text = text

            # Contador anti-loop
            replay_key = f"replay_count:{v_msg_id}"
            # CORREGIDO: Eliminado await.
            new_count = redis.incr(replay_key)
            redis.expire(replay_key, 600)

            if new_count > 3:
                return {"status": "replay_limit_reached_no_replay"}

            reconstructed_payload = {
                "message": {
                    "message_id": v_msg_id,
                    "from": {"username": v_sender},
                    "text": v_text,
                    "chat": {"id": message.get("chat", {}).get("id")}
                },
                "replay_meta": {"is_replay": True, "count": new_count}
            }

            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{vercel_url}/webhook",
                    json=reconstructed_payload,
                    headers={"X-M2M-Replay": "1"},
                    timeout=10.0
                )
