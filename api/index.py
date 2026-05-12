from fastapi import FastAPI, Request, HTTPException
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import os
import httpx
import logging
from datetime import datetime
from api.config import Config  # Importamos tu configuración personalizada

# Configuración de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- INSTANCIAS DE CLIENTES ---
# Usamos las variables centralizadas en Config
alpaca_client = TradingClient(Config.ALPACA_API_KEY, Config.ALPACA_SECRET_KEY, paper=Config.ALPACA_PAPER)

# --- HELPERS TELEGRAM ---
async def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": Config.TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        return r.json().get("result", {})

async def edit_telegram(msg_id: int, text: str):
    if not msg_id: return
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

# --- HELPERS UPSTASH (REDIS KV) ---
# Se corrigieron las cabeceras para usar el Token de Upstash
async def kv_command(method: str, endpoint: str, data: dict = None):
    headers = {"Authorization": f"Bearer {os.getenv('KV_REST_API_TOKEN')}"}
    url = f"{Config.REDIS_URL}{endpoint}"
    async with httpx.AsyncClient() as client:
        if method == "POST":
            r = await client.post(url, headers=headers, json=data)
        else:
            r = await client.get(url, headers=headers)
        return r.json().get("result")

async def kv_add_history(event: str):
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"history:{today}"
    log_line = f"{datetime.now().strftime('%H:%M:%S')} - {event}"
    await kv_command("POST", f"/lpush/{key}", {"element": log_line})
    await kv_command("POST", f"/ltrim/{key}", {"start": 0, "stop": 9})
    await kv_command("POST", f"/expire/{key}", {"seconds": 86400})

# --- LÓGICA DE EJECUCIÓN ---
async def ejecutar_orden_alpaca(ticker: str, side: str):
    try:
        # Calcular cantidad basada en RISK_PER_TRADE (ej: 0.01 = 1% de la cuenta)
        account = alpaca_client.get_account()
        equity = float(account.equity)
        monto_a_invertir = equity * Config.RISK_PER_TRADE
        
        # Obtener precio actual para calcular acciones
        # Nota: Simplificado para Market Order
        order_data = MarketOrderRequest(
            symbol=ticker,
            notional=monto_a_invertir, # Compra por dólares, no por acciones
            side=OrderSide.BUY if side == "BUY" else OrderSide.SELL,
            time_in_force=TimeInForce.GTC
        )
        
        order = alpaca_client.submit_order(order_data)
        return True, order.id
    except Exception as e:
        logger.error(f"Error Alpaca: {e}")
        return False, str(e)

# --- ENDPOINT ESTRATEGIA ---
@app.post("/strategy")
async def strategy_hub(req: Request):
    data = await req.json()
    
    # Validación de Seguridad M2M
    if data.get("api_key") != os.getenv("MAESTRO_M2M_SECRET"):
        return {"status": "unauthorized"}

    ticker = data.get("ticker", "").upper()
    bias = data.get("bias", "").upper() # BUY o SELL
    vix_actual = float(data.get("vix", 0))

    # 1. Filtro de Seguridad VIX
    if vix_actual > Config.MAX_VIX:
        await send_telegram(f"⚠️ *VETO VIX:* {ticker} cancelado.\nVIX Actual: `{vix_actual}`\nLímite: `{Config.MAX_VIX}`")
        return {"status": "vix_veto"}

    # 2. Iniciar flujo en Telegram
    res = await send_telegram(f"📡 *MONITOR:* Señal detectada\n🔍 *Activo:* {ticker} | *Bias:* {bias}\n⏳ *Estado:* Validando Consenso...")
    msg_id = res.get("message_id")

    # 3. Consenso en Redis (Necesita 2 votos de diferentes fuentes)
    source = data.get("source", "IA_Unknown")
    signal_key = f"signal:{ticker}:{bias}"
    
    await kv_command("POST", f"/sadd/{signal_key}", {"member": source})
    await kv_command("POST", f"/expire/{signal_key}", {"seconds": 300})
    voters = int(await kv_command("GET", f"/scard/{signal_key}") or 0)

    if voters >= 2:
        await edit_telegram(msg_id, f"🎯 *CONSENSO ALCANZADO* ({voters}/2)\n🚀 Ejecutando orden en Alpaca...")
        
        success, info = await ejecutar_orden_alpaca(ticker, bias)
        
        if success:
            await edit_telegram(msg_id, f"✅ *ORDEN COMPLETADA*\n📈 {ticker} {bias}\n💰 Riesgo: {Config.RISK_PER_TRADE * 100}%\n🆔 ID: `{info}`")
            await kv_add_history(f"EJECUTADO: {ticker} {bias}")
        else:
            await edit_telegram(msg_id, f"❌ *ERROR ALPACA*\n`{info}`")
    else:
        await edit_telegram(msg_id, f"📡 *MONITOR:* {ticker}\n⏳ *Votos:* {voters}/2. Esperando confirmación...")

    return {"status": "ok", "voters": voters}

# --- COMANDOS TELEGRAM ---
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    message = data.get("message", {})
    text = message.get("text", "")
    
    if text == "/balance":
        acc = alpaca_client.get_account()
        modo = "🧪 PAPER" if Config.ALPACA_PAPER else "💰 REAL"
        await send_telegram(f"📊 *CUENTA ALPACA ({modo})*\n\n💵 *Equity:* ${float(acc.equity):,.2f}\n💸 *Buying Power:* ${float(acc.buying_power):,.2f}")
        
    if text == "/start":
        await send_telegram(f"🤖 *Maestro AI Online*\n\nConfiguración actual:\n• VIX Máximo: `{Config.MAX_VIX}`\n• Riesgo: `{Config.RISK_PER_TRADE * 100}%`")
        
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "Maestro AI Online", "vix_limit": Config.MAX_VIX}
