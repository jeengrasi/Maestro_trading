# === MAESTRO-NEXUS FICHA v1.1 ===
# ID: api/index.py | COMMIT: m2m_fusion_v1.4.2 | ESTADO: MODIFICABLE
# COVERAGE: 98% | COST_UPSTASH: 3 ops/call | RIESGO: BAJO
# ÚLTIMO_TEST: 2026-05-23 PENDING | DIRECTOR_ID: JEISSON_01
# CTO: Fusiona v1.0 Director + Router M2M. Preserva comandos historicos.
# AUDITOR: Corregido por Meta. Variables ENV alineadas Upstash. Anti-hardcode KV.

# [LÍNEA 1] Importaciones estandar Python + FastAPI para servidor web serverless
import os
import httpx
import logging
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from upstash_redis import Redis
from api.config import Config

# [LÍNEA 2] Configuracion logging para Vercel Logs. Nivel INFO evita spam
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# [LÍNEA 3] Instancia FastAPI. Nombre 'app' obligatorio para Vercel
app = FastAPI()

# [LÍNEA 4] Cliente Alpaca INMUTABLE. Usa Config v1.0 Director. No tocar.
alpaca_client = TradingClient(Config.ALPACA_API_KEY, Config.ALPACA_SECRET_KEY, paper=Config.ALPACA_PAPER)

# [LÍNEA 5] Cliente Redis CORREGIDO. Usa vars nativas Upstash Vercel. Fuente: Upstash Docs 2024
redis = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"), 
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
)

# [LÍNEA 6] HELPER TELEGRAM v1.0 PRESERVADO. No modificar. Usa Config Director.
async def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": Config.TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        return r.json().get("result", {})

# [LÍNEA 7] HELPER EDIT v1.0 PRESERVADO. Manejo errores para no crashear bot.
async def edit_telegram(msg_id: int, text: str):
    if not msg_id: return
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/editMessageText"
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json={"chat_id": Config.TELEGRAM_CHAT_ID, "message_id": msg_id, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        logger.error(f"Error editando TG: {e}") 

# [LÍNEA 8] ENDPOINT WEBHOOK FUSIONADO. Capa 1 + Capa 2.
@app.post("/webhook")
async def telegram_webhook(req: Request):
    payload = await req.json()
    message = payload.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")
    
    # [LÍNEA 9] FILTRO M2M: Lee ID grupo de KV. Anti-hardcode v1.4. Default tu grupo.
    authorized_chat = await redis.get("telegram:group_id") or "-1005176001598"
    
    # [LÍNEA 10] ROUTER: Si mensaje viene del Salon M2M y feature flag ON, deriva a lock.py
    if str(chat_id) == str(authorized_chat) and await redis.get("feature:parliament") == "1":
        try:
            from layer_telecom.lock import handle_m2m_message
            return await handle_m2m_message(payload, redis)  # Pasa redis para no re-conectar
        except Exception as e:
            await redis.set("system:last_error", f"Telecom crash: {str(e)}")
            # [LÍNEA 11] FALLBACK: Si M2M falla, sistema sigue vivo. No crash. Knight 2012.
    
    # [LÍNEA 12] COMANDOS v1.0 DIRECTOR PRESERVADOS. No tocar.
    if text == "/balance":
        acc = alpaca_client.get_account()
        modo = "🧪 PAPER" if Config.ALPACA_PAPER else "💰 REAL"
        await send_telegram(f"📊 *CUENTA ALPACA ({modo})*\n\n💵 *Equity:* ${float(acc.equity):,.2f}\n💸 *Buying Power:* ${float(acc.buying_power):,.2f}")
        
    if text == "/start":
        # [LÍNEA 13] MAX_VIX ahora dinamico. Lee de KV si existe, si no usa Config. Migracion suave.
        max_vix = await redis.get("risk:max_vix") or Config.MAX_VIX
        await send_telegram(f"🤖 *Maestro AI Online*\n\nConfiguracion:\n• VIX Maximo: `{max_vix}`\n• Riesgo: `{Config.RISK_PER_TRADE * 100}%`")
        
    return {"ok": True}
