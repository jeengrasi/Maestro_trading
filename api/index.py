from fastapi import FastAPI, Request, HTTPException
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import os
import logging

# Config logging para ver errores en Vercel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 1. Variables de Entorno - Nunca van en código
ALPACA_KEY = os.environ.get("ALPACA_API_KEY")
ALPACA_SECRET = os.environ.get("ALPACA_SECRET_KEY")
ALPACA_PAPER = os.environ.get("ALPACA_PAPER", "true").lower() == "true"
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID")

# 2. Validación inicial - Si falta una key, el bot no arranca
if not all([ALPACA_KEY, ALPACA_SECRET, TG_TOKEN, TG_CHAT]):
    logger.error("Faltan variables de entorno críticas")
    raise HTTPException(status_code=500, detail="Missing environment variables")

# 3. Clientes
alpaca = TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=ALPACA_PAPER)
bot = Bot(token=TG_TOKEN)

# 4. Quitamos el startup_event para evitar spam. El bot responde solo por comandos.

@app.get("/")
async def root():
    """Healthcheck para Vercel"""
    try:
        account = alpaca.get_account()
        return {
            "status": "Maestro AI Online",
            "paper": ALPACA_PAPER,
            "cash": float(account.cash)
        }
    except Exception as e:
        logger.error(f"Error en root: {e}")
        return {"status": "Error", "detail": str(e)}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    """Webhook principal de Telegram. Aquí vive toda la lógica del Director."""
    try:
        data = await req.json()
        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = str(message.get("chat", {}).get("id", ""))

        # Seguridad: Solo responde a tu chat_id
        if chat_id != TG_CHAT:
            logger.warning(f"Intento de acceso de chat_id no autorizado: {chat_id}")
            return {"ok": True}

        # Comandos del Director
        if text == "/start":
            await bot.send_message(chat_id=TG_CHAT, text="👋 Maestro_Trading_AI listo. Usa /help para ver comandos.")
        
        elif text == "/help":
            ayuda = """
Comandos disponibles:
/balance - Ver saldo Paper Trading
/stop - Pausa total de emergencia
/status - Estado del bot y modo Paper
"""
            await bot.send_message(chat_id=TG_CHAT, text=ayuda)

        elif text == "/balance":
            account = alpaca.get_account()
            saldo = float(account.cash)
            equity = float(account.equity)
            msg = f"💰 Saldo Paper: ${saldo:,.2f}\n📊 Equity Total: ${equity:,.2f}"
            await bot.send_message(chat_id=TG_CHAT, text=msg)

        elif text == "/status":
            modo = "PAPER" if ALPACA_PAPER else "REAL ⚠️"
            msg = f"✅ Bot Online\nModo: {modo}\nMotor: FastAPI + Alpaca"
            await bot.send_message(chat_id=TG_CHAT, text=msg)

        elif text == "/stop":
            await bot.send_message(chat_id=TG_CHAT, text="🛑 Bot pausado por orden del Director. No se ejecutarán nuevas operaciones.")

        return {"ok": True}

    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        await bot.send_message(chat_id=TG_CHAT, text=f"❌ Error interno: {e}")
        return {"ok": True}

# 5. Endpoint para M2M - Fase siguiente con Gemini
@app.post("/strategy")
async def receive_strategy(req: Request):
    """
    Aquí Meta AI y Gemini van a enviar señales.
    Por ahora solo confirma recepción. En V1.2 mandamos el botón OK al Director.
    """
    try:
        data = await req.json()
        logger.info(f"Señal recibida: {data}")
        await bot.send_message(chat_id=TG_CHAT, text=f"🧠 Señal M2M recibida: {data.get('symbol')} {data.get('side')}. Fase de validación.")
        return {"status": "received", "data": data}
    except Exception as e:
        logger.error(f"Error en /strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))
