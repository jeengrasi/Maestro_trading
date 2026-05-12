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
from datetime import datetime, timedelta
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

def get_alpaca_trading():
    return TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=ALPACA_PAPER)

def get_alpaca_data():
    return StockHistoricalDataClient(ALPACA_KEY, ALPACA_SECRET)

async def send_telegram(text: str):
    if not TG_TOKEN or not TG_CHAT: return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": TG_CHAT, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True})

async def kv_set(key: str, value: dict, ex: int = 300):
    async with httpx.AsyncClient() as client:
        await client.post(f"{KV_URL}/set/{key}", headers={"Authorization": f"Bearer {KV_TOKEN}"}, json={"value": json.dumps(value), "ex": ex})

async def kv_get(key: str) -> Optional[dict]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{KV_URL}/get/{key}", headers={"Authorization": f"Bearer {KV_TOKEN}"})
        if r.status_code == 200 and r.json().get("result"):
            return json.loads(r.json()["result"])
    return None

async def kv_sadd(key: str, member: str, ex: int = 300):
    async with httpx.AsyncClient() as client:
        await client.post(f"{KV_URL}/sadd/{key}", headers={"Authorization": f"Bearer {KV_TOKEN}"}, json={"member": member})
        await client.post(f"{KV_URL}/expire/{key}", headers={"Authorization": f"Bearer {KV_TOKEN}"}, json={"seconds": ex})

async def kv_scard(key: str) -> int:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{KV_URL}/scard/{key}", headers={"Authorization": f"Bearer {KV_TOKEN}"})
        return int(r.json().get("result", 0))

async def kv_sismember(key: str, member: str) -> bool:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{KV_URL}/sismember/{key}/{member}", headers={"Authorization": f"Bearer {KV_TOKEN}"})
        return r.json().get("result") == 1

async def check_3lock_antispike(ticker: str) -> tuple[bool, str]:
    try:
        data_client = get_alpaca_data()
        bars_req = StockBarsRequest(symbol_or_symbols=ticker, timeframe=TimeFrame.Minute, limit=20)
        bars = data_client.get_stock_bars(bars_req).df
        if bars.empty: return False, "No data"

        latest = bars.iloc[-1]
        avg_vol = bars['volume'].mean()
        vwap = (bars['close'] * bars['volume']).sum() / bars['volume'].sum()

        # Lock 1: Volume Spike
        if latest['volume'] > 5 * avg_vol and (latest['close'] / bars.iloc[-4]['close'] - 1) > 0.015:
            return False, "LOCK1: Volume spike >5x + precio +1.5% en 3min"

        # Lock 2: RSI + VWAP Extension
        delta = bars['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        if rsi > 70 and latest['close'] > vwap * 1.02:
            return False, f"LOCK2: RSI {rsi:.1f} + 2% sobre VWAP"

        # Lock 3: Distancia a resistencia - simplificado: si subió 3% en 15min
        if (latest['close'] / bars.iloc[-15]['close'] - 1) > 0.03:
            return False, "LOCK3: +3% en 15min, posible techo"

        return True, "VERDE"
    except Exception as e:
        logger.error(f"Error 3-Lock: {e}")
        return False, f"Error técnico: {e}"

async def check_vix_lock() -> tuple[bool, str]:
    try:
        data_client = get_alpaca_data()
        vix_quote = data_client.get_stock_latest_quote(StockLatestQuoteRequest(symbol_or_symbols="VIX")).get("VIX")
        if vix_quote and vix_quote.bid_price > MAX_VIX:
            return False, f"LOCK4: VIX {vix_quote.bid_price} > {MAX_VIX}"
        return True, "VERDE"
    except:
        return True, "VIX no disponible, asumir VERDE"

async def check_daily_limits() -> tuple[bool, str]:
    today = datetime.now().strftime("%Y-%m-%d")
    trades_key = f"trades:{today}"
    trades_count = await kv_scard(trades_key) or 0
    if trades_count >= MAX_TRADES_PER_DAY:
        return False, f"Max {MAX_TRADES_PER_DAY} trades/día alcanzado"

    # Daily Loss Limit
    alpaca = get_alpaca_trading()
    account = alpaca.get_account()
    if float(account.equity) < float(account.last_equity) * 0.97:
        return False, "Kill-switch: -3% diario"
    return True, "OK"

def calculate_position_size(entry: float, stop: float) -> int:
    alpaca = get_alpaca_trading()
    account = alpaca.get_account()
    equity = float(account.equity)
    risk_amount = equity * RISK_PER_TRADE
    risk_per_share = abs(entry - stop)
    if risk_per_share == 0: return 0
    qty = int(risk_amount / risk_per_share)
    max_qty_by_capital = int((equity * 0.10) / entry) # Max 10% equity por trade
    return min(qty, max_qty_by_capital)

async def execute_order(ticker: str, qty: int, entry: float, stop: float, take: float, reason: str):
    try:
        alpaca = get_alpaca_trading()
        order = MarketOrderRequest(
            symbol=ticker,
            qty=qty,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
            order_class=OrderClass.BRACKET,
            stop_loss=StopLossRequest(stop_price=stop),
            take_profit=TakeProfitRequest(limit_price=take)
        )
        alpaca.submit_order(order)

        today = datetime.now().strftime("%Y-%m-%d")
        await kv_sadd(f"trades:{today}", ticker, ex=86400)

        await send_telegram(f"🤖 *AUTO-EJECUTADO*\n──────────────\n*TICKER:* {ticker}\n*QTY:* {qty}\n*Entrada:* ${entry:.2f}\n*SL:* ${stop:.2f}\n*TP:* ${take:.2f}\n*Riesgo:* {RISK_PER_TRADE*100:.0f}%\n*Razón:* {reason}")
        logger.info(f"Orden ejecutada: {ticker} {qty}")
    except Exception as e:
        logger.error(f"Error ejecutando: {e}")
        await send_telegram(f"❌ *ERROR EJECUCIÓN {ticker}*\n{str(e)}")

@app.post("/strategy")
async def strategy_hub(req: Request):
    data = await req.json()

    # 1. Auth M2M
    if data.get("api_key")!= M2M_SECRET:
        raise HTTPException(401, "Unauthorized")

    source = data.get("source")
    ticker = data.get("ticker", "").upper()
    bias = data.get("bias", "").upper()

    if not all([source, ticker, bias]):
        raise HTTPException(400, "Missing fields")

    # 2. Check Safeguards globales
    limits_ok, limits_msg = await check_daily_limits()
    if not limits_ok:
        await send_telegram(f"🛑 *KILL-SWITCH*: {limits_msg}")
        return {"status": "blocked", "reason": limits_msg}

    vix_ok, vix_msg = await check_vix_lock()
    if not vix_ok:
        await kv_sadd(f"signal:{ticker}:VETO", "VIX_LOCK", ex=300)
        await send_telegram(f"⚠️ *VETO MACRO*: {vix_msg}. Señal {ticker} bloqueada.")
        return {"status": "veto", "reason": vix_msg}

    # 3. Procesar voto
    signal_key = f"signal:{ticker}:{bias}"
    vote_key = f"vote:{ticker}:{bias}:{source}"

    if bias == "VETO":
        await kv_set(signal_key, {"status": "VETO", "reason": data.get("reason", "Veto IA")}, ex=300)
        await send_telegram(f"🛑 *VETO ACTIVADO* {ticker}\nPor: {source}\nRazón: {data.get('reason')}")
        return {"status": "veto"}

    await kv_sadd(signal_key, source, ex=300)
    await kv_set(vote_key, data, ex=300)

    # 4. Check Consenso
    voters = await kv_scard(signal_key)
    has_veto = await kv_get(f"signal:{ticker}:VETO")

    if has_veto:
        return {"status": "blocked", "reason": "VETO activo"}

    if voters >= 2:
        # 5. Meta AI hace validación técnica si el voto no es mío
        if source!= "Meta":
            tech_ok, tech_msg = await check_3lock_antispike(ticker)
            if not tech_ok:
                await kv_set(f"signal:{ticker}:VETO", {"status": "VETO", "reason": tech_msg}, ex=300)
                await send_telegram(f"🛑 *VETO TÉCNICO* {ticker}\n{tech_msg}")
                return {"status": "veto", "reason": tech_msg}
            await kv_sadd(signal_key, "Meta", ex=300)

        # 6. CONSENSO ALCANZADO - EJECUTAR
        # Buscar datos de la señal para SL/TP
        signal_data = await kv_get(f"vote:{ticker}:{bias}:Gemini") or await kv_get(f"vote:{ticker}:{bias}:Meta") or data
        entry = float(signal_data.get("entry", 0))
        stop = float(signal_data.get("stop_loss", 0))
        take = float(signal_data.get("take_profit", 0))

        if entry > 0 and stop > 0:
            qty = calculate_position_size(entry, stop)
            if qty > 0:
                reason = f"{source} + Meta | {signal_data.get('catalyst_type', 'N/A')}"
                if AUTO_EXECUTE:
                    await execute_order(ticker, qty, entry, stop, take, reason)
                    return {"status": "executed", "ticker": ticker, "qty": qty}
                else:
                    await send_telegram(f"🎯 *CONSENSO M2M: {ticker}*\n{reason}\n\n[✅ EJECUTAR] - Manual")
                    return {"status": "consensus", "action": "manual"}

    return {"status": "voted", "votes": voters, "need": 2}

@app.get("/")
async def root():
    alpaca = get_alpaca_trading()
    account = alpaca.get_account()
    return {"status":"Maestro AI Online","mode":"Full Auto" if AUTO_EXECUTE else "Semi-Auto","equity":float(account.equity)}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    text = data.get("message", {}).get("text", "")
    if text == "/balance":
        alpaca = get_alpaca_trading()
        account = alpaca.get_account()
        await send_telegram(f"💰 *Equity:* ${float(account.equity):,.2f}\n📊 *Cash:* ${float(account.cash):,.2f}\n🤖 *Modo:* {'Full Auto' if AUTO_EXECUTE else 'Semi-Auto'}")
    return {"ok": True}
