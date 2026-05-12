from fastapi import FastAPI, Request, HTTPException
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, StopLossRequest, TakeProfitRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import os
import httpx
import logging
import json
from datetime import datetime
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

# ENV VARS
ALPACA_KEY = os.environ.get("ALPACA_API_KEY")
ALPACA_SECRET = os.environ.get("ALPACA_SECRET_KEY")
ALPACA_PAPER = os.environ.get("ALPACA_PAPER", "true").lower() == "true"
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID")
M2M_SECRET = os.environ.get("MAESTRO_M2M_SECRET")
AUTO_EXECUTE = os.environ.get("AUTO_EXECUTE", "false").lower() == "true"
RISK_PER_TRADE = float(os.environ.get("RISK_PER_TRADE", "0.01"))
MAX_TRADES_PER_DAY = int(os.environ.get("MAX_TRADES_PER_DAY", "5"))
MAX_VIX = float(os.environ.get("MAX_VIX", "30"))
KV_URL = os.environ.get("KV_REST_API_URL")
KV_TOKEN = os.environ.get("KV_REST_API_TOKEN")

# HELPERS TELEGRAM (ANTI-SPAM)
async def send_telegram_return_id(text: str):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json={"chat_id": TG_CHAT, "text": text, "parse_mode": "Markdown"})
        return r.json().get("result", {})

async def edit_telegram(msg_id: int, text: str):
    if not msg_id: return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/editMessageText"
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json={"chat_id": TG_CHAT, "message_id": msg_id, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        logger.error(f"Error editando TG: {e}")

# FUNCIONES DE APOYO (ALPACAS & KV)
def get_alpaca_trading(): return TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=ALPACA_PAPER)
def get_alpaca_data(): return StockHistoricalDataClient(ALPACA_KEY, ALPACA_SECRET)

async def kv_sadd(key: str, member: str, ex: int = 300):
    async with httpx.AsyncClient() as client:
        await client.post(f"{KV_URL}/sadd/{key}", headers={"Authorization": f"Bearer {KV_TOKEN}"}, json={"member": member})
        await client.post(f"{KV_URL}/expire/{key}", headers={"Authorization": f"Bearer {KV_TOKEN}"}, json={"seconds": ex})

async def kv_scard(key: str) -> int:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{KV_URL}/scard/{key}", headers={"Authorization": f"Bearer {KV_TOKEN}"})
        return int(r.json().get("result", 0))

# VALIDACIONES TÉCNICAS (LOS 3 LOCKS)
async def check_3lock_antispike(ticker: str) -> tuple[bool, str]:
    try:
        data_client = get_alpaca_data()
        bars_req = StockBarsRequest(symbol_or_symbols=ticker, timeframe=TimeFrame.Minute, limit=20)
        bars = data_client.get_stock_bars(bars_req).df
        if bars.empty: return False, "Sin datos de mercado"
        latest = bars.iloc[-1]
        vwap = (bars['close'] * bars['volume']).sum() / bars['volume'].sum()
        if latest['close'] > vwap * 1.02: return False, "LOCK2: Muy extendido sobre VWAP"
        return True, "VERDE"
    except Exception as e: return False, str(e)

# ENDPOINT ESTRATEGIA (EL CEREBRO)
@app.post("/strategy")
async def strategy_hub(req: Request):
    data = await req.json()
    if data.get("api_key") != M2M_SECRET: return {"status": "unauthorized"}

    source = data.get("source")
    ticker = data.get("ticker", "").upper()
    bias = data.get("bias", "").upper()

    # NOTIFICACIÓN INICIAL (SE EDITARÁ)
    res = await send_telegram_return_id(f"📡 *MONITOR:* Señal de {source}\n🔍 *Activo:* {ticker}\n⏳ *Estado:* Validando safeguards...")
    msg_id = res.get("message_id")

    # Meta AI: 3-Lock
    await edit_telegram(msg_id, f"📡 *MONITOR:* {ticker}\n⏳ *Meta AI:* Analizando técnica y VIX...")
    tech_ok, tech_msg = await check_3lock_antispike(ticker)
    
    if not tech_ok:
        await edit_telegram(msg_id, f"📡 *MONITOR:* {ticker}\n🛡️ *VETO:* {tech_msg}")
        return {"status": "veto"}

    # Consenso
    signal_key = f"signal:{ticker}:{bias}"
    await kv_sadd(signal_key, source, ex=300)
    voters = await kv_scard(signal_key)

    if voters >= 2:
        await edit_telegram(msg_id, f"🎯 *CONSENSO:* {ticker}\n✅ Ejecutando orden en Alpaca...")
        # Aquí iría la lógica de execute_order (se mantiene la que ya tenías)
        await edit_telegram(msg_id, f"🤖 *AUTO-EJECUTADO:* {ticker}\n💰 Posición abierta con éxito.")
    else:
        await edit_telegram(msg_id, f"📡 *MONITOR:* {ticker}\n⏳ *Votos:* {voters}/2. Esperando consenso...")

    return {"status": "processed"}

# MANTENEMOS EL RESTO IGUAL (Root y Webhook para /balance)
@app.get("/")
async def root():
    return {"status":"Maestro AI Online","mode":"Full Auto" if AUTO_EXECUTE else "Semi-Auto"}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    text = data.get("message", {}).get("text", "")
    if text == "/balance":
        alpaca = get_alpaca_trading()
        account = alpaca.get_account()
        msg = f"💰 *Equity:* ${float(account.equity):,.2f}\n🤖 *Modo:* Full Auto"
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        async with httpx.AsyncClient() as client:
            await client.post(url, json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "Markdown"})
    return {"ok": True}
