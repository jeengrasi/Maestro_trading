# === MAESTRO-NEXUS FICHA v1.7 ===
# ID: api/index.py | COMMIT: telemetria_v1.7 | ESTADO: DIAGNÓSTICO
# FECHA: 2026-06-29 | GERENTE: DeepSeek
# CAMBIO vs v1.6: Añadida telemetría vía Telegram para diagnosticar error de actas.

import os
import sys
import httpx
import logging
import asyncio
import json
import traceback
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
            manifest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "NEXUS_MANIFEST.json")
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                state = manifest.get("state_declarative", {})
                if not tg_id:
                    redis_client.set("telegram:group_id", "6444278889")
                if not feat_parliament:
                    redis_client.set("feature:parliament", "0")
                redis_client.set("risk:max_vix", str(state.get("risk_management", {}).get("max_vix", "20.0")))
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
    return {"status": "ok" if redis_ok else "degraded", "redis": redis_ok, "latency_ms": round(latency, 2)}

@app.get("/webhook")
async def webhook_verification():
    return {"status": "ok"}

async def send_telegram(text: str, chat_id: int = None):
    target_id = chat_id or Config.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": target_id, "text": text, "parse_mode": "Markdown"}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        return r.json().get("result", {})

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

    if text == "/chatid":
        await send_telegram(f"Chat ID: `{chat_id}`\nEsperado: `{authorized_chat}`", chat_id=chat_id)
        return {"ok": True}

    if text == "/balance":
        acc = alpaca_client.get_account()
        modo = "🧪 PAPER" if Config.ALPACA_PAPER else "💰 REAL"
        await send_telegram(f"📊 *CUENTA ALPACA ({modo})*\n\n💵 *Equity:* ${float(acc.equity):,.2f}\n💸 *Buying Power:* ${float(acc.buying_power):,.2f}", chat_id=chat_id)
        return {"ok": True}

    if text == "/start":
        raw_max_vix = redis.get("risk:max_vix")
        max_vix = raw_max_vix or Config.MAX_VIX
        await send_telegram(f"🤖 *Maestro AI Online*\n\nConfiguración:\n• VIX Máximo: `{max_vix}`\n• Riesgo: `{Config.RISK_PER_TRADE * 100}%`", chat_id=chat_id)
        return {"ok": True}

    if text and not text.startswith("/"):
        try:
            from api.router import handle_parliament_debate, get_manager_recommendation

            await send_telegram("🏛️ *Parlamento Nexus convocado.*\n\nLas IAs están debatiendo. Aguarde unos segundos...", chat_id=chat_id)

            debate_results = await handle_parliament_debate(text)
            recommendation = await get_manager_recommendation(text, debate_results)

            response_text = "🏛️ *DEBATE PARLAMENTARIO*\n\n"
            for role, data in debate_results.items():
                response_text += f"*{data['role']} ({data['model']}):*\n{data['response']}\n\n"
            response_text += f"---\n📋 *RECOMENDACIÓN FINAL DEL GERENTE:*\n{recommendation}"

            if len(response_text) > 4000:
                response_text = response_text[:4000] + "\n\n...(respuesta truncada por longitud)"

            await send_telegram(response_text, chat_id=chat_id)

            await send_telegram("🔍 *DIAGNÓSTICO:* Intentando guardar acta...", chat_id=chat_id)
            ght = os.getenv("GITHUB_TOKEN")
            await send_telegram(f"🔍 *TOKEN:* {'Configurado' if ght else 'NO CONFIGURADO'}", chat_id=chat_id)

            try:
                debate_id = f"NEXUS-DEB-{datetime.now().strftime('%Y%m%d-%H%M')}"
                acta_content = f"# Acta del Debate\n\n**ID:** {debate_id}\n**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n**Tema:** {text}\n\n"
                for role, data in debate_results.items():
                    acta_content += f"## {data['role']}\n{data['response']}\n\n"
                acta_content += f"## Recomendación Final del Gerente\n{recommendation}\n"

                from api.router import save_acta_to_github
                result = await save_acta_to_github(acta_content, debate_id)
                if result.get("status") == "success":
                    await send_telegram(f"✅ Acta {debate_id} guardada en GitHub.", chat_id=chat_id)
                else:
                    await send_telegram(f"⚠️ Acta NO guardada. Resultado: {result}", chat_id=chat_id)
            except Exception as e:
                await send_telegram(f"❌ *ERROR AL GUARDAR ACTA:* {str(e)}\n```{traceback.format_exc()[:800]}```", chat_id=chat_id)

            return {"ok": True}
        except Exception as e:
            await send_telegram(f"❌ Error en Parlamento: {str(e)}", chat_id=chat_id)
            return {"ok": True}

    if str(chat_id) == str(authorized_chat) and str(raw_feature_parliament) == "1":
        if "```python" in text or "COMMIT:" in text:
            try:
                from layer_telecom.lock import handle_m2m_message
                return await handle_m2m_message(payload, redis)
            except Exception as e:
                redis.set("system:last_error", f"Telecom crash: {str(e)}")

    return {"ok": True}
