# === MAESTRO-NEXUS FICHA v1.7 ===
# ID: api/index.py | COMMIT: memory_v1.7 | ESTADO: CORREGIDO
# FECHA: 2026-06-30 | GERENTE: DeepSeek
# CAMBIO vs v1.6: Memoria en 3 niveles (Redis, GitHub)

import os, sys, httpx, logging, asyncio, json
from datetime import datetime
from fastapi import FastAPI, Request
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from upstash_redis import Redis
from api.config import Config
from api.telegram.utils import send_telegram

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

redis = Redis(url=os.getenv("UPSTASH_REDIS_REST_URL"), token=os.getenv("UPSTASH_REDIS_REST_TOKEN"))
alpaca_client = TradingClient(Config.ALPACA_API_KEY, Config.ALPACA_SECRET_KEY, paper=Config.ALPACA_PAPER)

def bootstrap_nexus_memory(redis_client: Redis):
    try:
        tg_id = redis_client.get("telegram:group_id")
        feat_parliament = redis_client.get("feature:parliament")
        if not tg_id or not feat_parliament:
            manifest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "NEXUS_MANIFEST.json")
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f: manifest = json.load(f)
                state = manifest.get("state_declarative", {})
                if not tg_id: redis_client.set("telegram:group_id", "6444278889")
                if not feat_parliament: redis_client.set("feature:parliament", "0")
                redis_client.set("risk:max_vix", str(state.get("risk_management", {}).get("max_vix", "20.0")))
                redis_client.set("nexus:state:last_recovery", datetime.now().isoformat())
                logger.info("Redis auto-hidratado.")
    except Exception as e:
        logger.error(f"Error memoria: {e}", exc_info=True)

@app.get("/")
async def root(): return {"status": "running", "system": "Maestro-Nexus"}

@app.get("/health")
async def health():
    start = datetime.now()
    try:
        r = await asyncio.wait_for(asyncio.to_thread(redis.ping), timeout=2.0)
        redis_ok = (r == "PONG" or r is True)
    except: redis_ok = False
    return {"status": "ok" if redis_ok else "degraded", "redis": redis_ok, "latency_ms": round((datetime.now() - start).total_seconds() * 1000, 2)}

@app.get("/webhook")
async def webhook_verification(): return {"status": "ok"}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    payload = await req.json()
    message = payload.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")
    bootstrap_nexus_memory(redis)
    raw_authorized_chat = redis.get("telegram:group_id")
    authorized_chat = raw_authorized_chat or "6444278889"

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
            from api.router import handle_parliament_debate, get_manager_recommendation, classify_intent, call_ia
            intent = classify_intent(text)
            if intent["confidence"] >= 1:
                await send_telegram("🏛️ *Parlamento Nexus convocado.*\n\nLas IAs están debatiendo...", chat_id=chat_id)
                debate_results = await handle_parliament_debate(text)
                recommendation = await get_manager_recommendation(text, debate_results)
                response_text = "🏛️ *DEBATE PARLAMENTARIO*\n\n"
                for role, data in debate_results.items():
                    response_text += f"*{data['role']} ({data['model']}):*\n{data['response']}\n\n"
                response_text += f"---\n📋 *RECOMENDACIÓN FINAL:*\n{recommendation}"
            else:
                role = intent["role"]
                dept_name = intent["department"].capitalize()
                await send_telegram(f"🤖 *Consultando al departamento de {dept_name}...*", chat_id=chat_id)
                response = await call_ia(role, text)
                response_text = f"🏛️ *{dept_name}*\n\n{response}"
            if len(response_text) > 4000: response_text = response_text[:4000] + "\n\n...(truncado)"
            await send_telegram(response_text, chat_id=chat_id)

            # === MEMORIA CORTO PLAZO (Redis) ===
            redis.set("memory:last_debate", json.dumps({
                "tema": text, "fecha": datetime.now().isoformat(),
                "respuesta": response_text[:500]
            }))
            redis.expire("memory:last_debate", 86400)

            # === MEMORIA MEDIANO PLAZO (GitHub) ===
            try:
                from api.router import save_acta_to_github
                acta_data = {
                    "id": f"NEXUS-DEB-{datetime.now().strftime('%Y%m%d-%H%M')}",
                    "fecha": datetime.now().isoformat(),
                    "tema": text,
                    "respuesta": response_text[:2000]
                }
                await save_acta_to_github(json.dumps(acta_data, indent=2), acta_data["id"])
            except Exception as e:
                logger.warning(f"No se pudo guardar acta: {e}")

            return {"ok": True}
        except Exception as e:
            logger.error(f"Error Parlamento: {e}", exc_info=True)
            await send_telegram(f"❌ Error: {str(e)}", chat_id=chat_id)
            return {"ok": True}

    if str(chat_id) == str(authorized_chat) and redis.get("feature:parliament") == "1":
        if "```python" in text or "COMMIT:" in text:
            try:
                from layer_telecom.lock import handle_m2m_message
                return await handle_m2m_message(payload, redis)
            except Exception as e:
                redis.set("system:last_error", f"Telecom crash: {str(e)}")

    return {"ok": True}
