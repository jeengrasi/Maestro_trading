# === MAESTRO-NEXUS FICHA v1.5 ===
# ID: api/index.py | COMMIT: fix_parliament_flow_v1.5 | ESTADO: CORREGIDO
# FECHA: 2026-06-28 | GERENTE: DeepSeek
# CAMBIO: El Parlamento se ejecuta ANTES que lock.py para mensajes normales.
# lock.py solo se ejecuta si el mensaje contiene código Python o COMMIT.

import os
import sys
import httpx
import logging
import asyncio
import json
from datetime import datetime
from fastapi import FastAPI, Request
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from upstash_redis import Redis
from api.config import Config

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

redis = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
)

alpaca_client = TradingClient(
    Config.ALPACA_API_KEY,
    Config.ALPACA_SECRET_KEY,
    paper=Config.ALPACA_PAPER
)

def bootstrap_nexus_memory(redis_client: Redis):
    try:
        tg_id = redis_client.get("telegram:group_id")
        feat_parliament = redis_client.get("feature:parliament")

        if not tg_id or not feat_parliament:
            manifest_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "NEXUS_MANIFEST.json"
            )

            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)

                state = manifest.get("state_declarative", {})
                tg_key = state.get("telegram_group_id_key", "telegram:group_id")
                feat_key = state.get("feature_parliament_key", "feature:parliament")
                max_vix = state.get("risk_management", {}).get("max_vix", "20.0")

                if not tg_id:
                    redis_client.set(tg_key, "6444278889")
                if not feat_parliament:
                    redis_client.set(feat_key, "0")

                redis_client.set("risk:max_vix", str(max_vix))
                redis_client.set("nexus:state:last_recovery", datetime.now().isoformat())

                logger.info("⚙️ MEMORIA NEXUS: Redis auto-hidratado exitosamente.")
    except Exception as e:
        logger.error(f"❌ Error en engranaje de memoria: {e}", exc_info=True)

@app.get("/")
async def root():
    return {"status": "running", "system": "Maestro-Nexus"}

@app.get("/health")
async def health():
    start = datetime.now()
    redis_ok = False
    try:
        r = await asyncio.wait_for(asyncio.to_thread(redis.ping), timeout=2.0)
        redis_ok = (r == "PONG" or r is True)
    except Exception as e:
        logger.error(f"Fallo Upstash en /health: {e}")
        redis_ok = False
    latency = (datetime.now() - start).total_seconds() * 1000
    return {
        "status": "ok" if redis_ok else "degraded",
        "redis": redis_ok,
        "latency_ms": round(latency, 2)
    }

@app.get("/webhook")
async def webhook_verification():
    return {"status": "ok"}

async def send_telegram(text: str, chat_id: int = None):
    target_id = chat_id or Config.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": target_id, "text": text, "parse_mode": "Markdown"}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        logger.info(f"TG_SEND status={r.status_code} to={target_id}")
        return r.json().get("result", {})

async def edit_telegram(msg_id: int, text: str):
    if not msg_id:
        return
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/editMessageText"
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json={
                "chat_id": Config.TELEGRAM_CHAT_ID,
                "message_id": msg_id,
                "text": text,
                "parse_mode": "Markdown"
            })
    except Exception as e:
        logger.error(f"Error editando TG: {e}")

@app.post("/webhook")
async def telegram_webhook(req: Request):
    payload = await req.json()
    message = payload.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    bootstrap_nexus_memory(redis)

    raw_authorized_chat = redis.get("telegram:group_id")
    authorized_chat = raw_authorized_chat or "6444278889"
    raw_feature_parliament = redis.get("feature:parliament")

    logger.info(json.dumps({
        "event": "webhook_auth_check",
        "incoming_chat_id": chat_id,
        "authorized_chat_id": authorized_chat,
        "feature_parliament": raw_feature_parliament,
        "match": str(chat_id) == str(authorized_chat)
    }))

    # === COMANDOS DIRECTOS ===
    if text == "/chatid":
        await send_telegram(
            f"Chat ID: `{chat_id}`\nEsperado: `{authorized_chat}`",
            chat_id=chat_id
        )
        return {"ok": True}

    if text == "/balance":
        acc = alpaca_client.get_account()
        modo = "🧪 PAPER" if Config.ALPACA_PAPER else "💰 REAL"
        await send_telegram(
            f"📊 *CUENTA ALPACA ({modo})*\n\n"
            f"💵 *Equity:* ${float(acc.equity):,.2f}\n"
            f"💸 *Buying Power:* ${float(acc.buying_power):,.2f}",
            chat_id=chat_id
        )
        return {"ok": True}

    if text == "/start":
        raw_max_vix = redis.get("risk:max_vix")
        max_vix = raw_max_vix or Config.MAX_VIX
        await send_telegram(
            f"🤖 *Maestro AI Online*\n\n"
            f"Configuración:\n"
            f"• VIX Máximo: `{max_vix}`\n"
            f"• Riesgo: `{Config.RISK_PER_TRADE * 100}%`",
            chat_id=chat_id
        )
        return {"ok": True}

    # === CHAT PARLAMENTARIO: MENSAJES NORMALES (ANTES QUE LOCK) ===
    if text and not text.startswith("/"):
        try:
            from api.router import handle_parliament_debate, get_manager_recommendation

            await send_telegram(
                "🏛️ *Parlamento Nexus convocado.*\n\nLas IAs están debatiendo. Aguarde unos segundos...",
                chat_id=chat_id
            )

            debate_results = await handle_parliament_debate(text)
            recommendation = await get_manager_recommendation(text, debate_results)

            response_text = "🏛️ *DEBATE PARLAMENTARIO*\n\n"
            for role, data in debate_results.items():
                response_text += f"*{data['role']} ({data['model']}):*\n{data['response']}\n\n"
            response_text += f"---\n📋 *RECOMENDACIÓN FINAL DEL GERENTE:*\n{recommendation}"

            if len(response_text) > 4000:
                response_text = response_text[:4000] + "\n\n...(respuesta truncada por longitud)"

            await send_telegram(response_text, chat_id=chat_id)
            return {"ok": True}
        except Exception as e:
            logger.error(f"Error en Parlamento: {e}", exc_info=True)
            await send_telegram(
                f"❌ Error al procesar el debate parlamentario: {str(e)}",
                chat_id=chat_id
            )
            return {"ok": True}

    # === MODO PARLAMENTO: STAGING DE CÓDIGO (SOLO SI TIENE CÓDIGO) ===
    if str(chat_id) == str(authorized_chat) and str(raw_feature_parliament) == "1":
        if "```python" in text or "COMMIT:" in text:
            try:
                from layer_telecom.lock import handle_m2m_message
                return await handle_m2m_message(payload, redis)
            except Exception as e:
                redis.set("system:last_error", f"Telecom crash: {str(e)}")
                logger.error(f"Fallo crítico en layer_telecom: {e}", exc_info=True)

    return {"ok": True}
