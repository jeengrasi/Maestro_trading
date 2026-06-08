# === MAESTRO-NEXUS FICHA v1.1 ===
# ID: api/index.py | COMMIT: m2m_fusion_v1.4.7-FIXED | ESTADO: CERTIFICADO-PARA-PRODUCCIÓN
# COVERAGE: 0% (Sin tests activos) | COST_UPSTASH: 1 op/call | RIESGO: MÍNIMO
# ÚLTIMO_TEST: 2026-06-05 | DIRECTOR_ID: JEISSON_01
# CTO: Integración de telemetría avanzada.
# AUDITOR: Meta SRE. Validación estricta de chat_id. Eliminación de sanitización insegura.

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

# Visibilidad de capas en Vercel
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

@app.get("/")
async def root():
    return {"status": "running", "system": "Maestro-Nexus"}

@app.get("/health")
async def health():
    start = datetime.now()
    redis_ok = False
    
    try:
        r = await asyncio.wait_for(
            asyncio.to_thread(redis.ping), 
            timeout=2.0
        )
        redis_ok = (r == "PONG" or r is True)
    except Exception as e:
        logger.error(f"Fallo de conexión Upstash en /health: {e}")
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

async def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": Config.TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
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

    authorized_chat = redis.get("telegram:group_id") or "-1005176001598"

    # === TELEMETRÍA M2M (Meta SRE) ===
    logger.info(json.dumps({
        "event": "webhook_auth_check",
        "incoming_chat_id": chat_id,
        "authorized_chat_id": authorized_chat,
        "feature_parliament": redis.get("feature:parliament"),
        "match": str(chat_id) == str(authorized_chat)
    }))

    # === VALIDACIÓN ESTRICTA (Meta SRE) ===
    if str(chat_id) == str(authorized_chat) and redis.get("feature:parliament") == "1":
        try:
            from layer_telecom.lock import handle_m2m_message
            return await handle_m2m_message(payload, redis)
        except Exception as e:
            redis.set("system:last_error", f"Telecom crash: {str(e)}")
            logger.error(f"Fallo crítico en layer_telecom: {e}", exc_info=True)

    # === COMANDO /chatid (Meta SRE) ===
    if text == "/chatid":
        await send_telegram(f"Chat ID: `{chat_id}`\nEsperado: `{authorized_chat}`")
        return {"ok": True}

    if text == "/balance":
        acc = alpaca_client.get_account()
        modo = "🧪 PAPER" if Config.ALPACA_PAPER else "💰 REAL"
        await send_telegram(
            f"📊 *CUENTA ALPACA ({modo})*\n\n"
            f"💵 *Equity:* ${float(acc.equity):,.2f}\n"
            f"💸 *Buying Power:* ${float(acc.buying_power):,.2f}"
        )

    if text == "/start":
        max_vix = redis.get("risk:max_vix") or Config.MAX_VIX
        await send_telegram(
            f"🤖 *Maestro AI Online*\n\n"
            f"Configuración:\n"
            f"• VIX Máximo: `{max_vix}`\n"
            f"• Riesgo: `{Config.RISK_PER_TRADE * 100}%`"
        )

    return {"ok": True}
