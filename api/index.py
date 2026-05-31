# === MAESTRO-NEXUS FICHA v1.1 ===
# ID: api/index.py | COMMIT: m2m_fusion_v1.4.5-PROD | ESTADO: CRÍTICO-REPARADO
# COVERAGE: 0% (Sin tests activos) | COST_UPSTASH: 1 op/call | RIESGO: MÍNIMO
# ÚLTIMO_TEST: 2026-05-30 | DIRECTOR_ID: JEISSON_01
# CTO: Integrado fix de asyncio de la mesa. Prevención de bloqueo de event loop.
# AUDITOR: Meta SRE. Health con timeout de 2s y aislamiento de hilo (to_thread).

# [LÍNEA 1] Importaciones estándar
import os
import httpx
import logging
import asyncio  # Añadido por consenso del Parlamento M2M
from datetime import datetime
from fastapi import FastAPI, Request
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from upstash_redis import Redis
from api.config import Config

# [LÍNEA 2] Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# [LÍNEA 3] Instancia FastAPI
app = FastAPI()

# [LÍNEA 4] Cliente Redis
redis = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
)

# [LÍNEA 5] Cliente Alpaca
alpaca_client = TradingClient(
    Config.ALPACA_API_KEY,
    Config.ALPACA_SECRET_KEY,
    paper=Config.ALPACA_PAPER
)

# === ENDPOINT RAÍZ (SRE-SUGERIDO) ===
@app.get("/")
async def root():
    return {"status": "running", "system": "Maestro-Nexus"}

# === HEALTHCHECK v1.2 (100/100 PARLAMENTO-APROBADO) ===
@app.get("/health")
async def health():
    start = datetime.now()
    redis_ok = False
    
    try:
        # Ejecuta el ping síncrono en un hilo separado para no bloquear FastAPI
        # Protegido con un timeout estricto de 2.0 segundos
        r = await asyncio.wait_for(
            asyncio.to_thread(redis.ping), 
            timeout=2.0
        )
        redis_ok = (r == "PONG" or r is True)
    except Exception as e:
        logger.error(f"Fallo de conexión Upstash en /health: {e}")
        redis_ok = False

    # 2. Latencia
    latency = (datetime.now() - start).total_seconds() * 1000

    # 3. Respuesta JSON
    return {
        "status": "ok" if redis_ok else "degraded",
        "redis": redis_ok,
        "latency_ms": round(latency, 2)
    }

# [LÍNEA 6] Helper Telegram
async def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": Config.TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        return r.json().get("result", {})

# [LÍNEA 7] Helper Edit Telegram
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

# === WEBHOOK PRINCIPAL ===
@app.post("/webhook")
async def telegram_webhook(req: Request):
    payload = await req.json()
    message = payload.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    # [LÍNEA 9] Filtro M2M
    # Nota SRE: Ejecución síncrona temporal aceptada únicamente para fase P0
    authorized_chat = redis.get("telegram:group_id") or "-1005176001598"

    # [LÍNEA 10] Router M2M
    if str(chat_id) == str(authorized_chat) and redis.get("feature:parliament") == "1":
        try:
            from layer_telecom.lock import handle_m2m_message
            return await handle_m2m_message(payload, redis)
        except Exception as e:
            redis.set("system:last_error", f"Telecom crash: {str(e)}")

    # [LÍNEA 12] Comando /balance
    if text == "/balance":
        acc = alpaca_client.get_account()
        modo = "🧪 PAPER" if Config.ALPACA_PAPER else "💰 REAL"
        await send_telegram(
            f"📊 *CUENTA ALPACA ({modo})*\n\n"
            f"💵 *Equity:* ${float(acc.equity):,.2f}\n"
            f"💸 *Buying Power:* ${float(acc.buying_power):,.2f}"
        )

    # [LÍNEA 13] Comando /start
    if text == "/start":
        max_vix = redis.get("risk:max_vix") or Config.MAX_VIX
        await send_telegram(
            f"🤖 *Maestro AI Online*\n\n"
            f"Configuración:\n"
            f"• VIX Máximo: `{max_vix}`\n"
            f"• Riesgo: `{Config.RISK_PER_TRADE * 100}%`"
        )

    return {"ok": True}
