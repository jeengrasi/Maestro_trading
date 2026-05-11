from fastapi import FastAPI, Request
from alpaca.trading.client import TradingClient
from telegram import Bot
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 1. Solo leemos las variables. No validamos ni conectamos aquí.
ALPACA_KEY = os.environ.get("ALPACA_API_KEY")
ALPACA_SECRET = os.environ.get("ALPACA_SECRET_KEY")
ALPACA_PAPER = os.environ.get("ALPACA_PAPER", "true").lower() == "true"
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID")

# 2. Funciones que crean los clientes solo cuando se necesitan
def get_alpaca():
    if not ALPACA_KEY or not ALPACA_SECRET:
        raise ValueError("Faltan ALPACA_API_KEY o ALPACA_SECRET_KEY en Vercel")
    return TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=ALPACA_PAPER)

def get_bot():
    if not TG_TOKEN:
        raise ValueError("Falta TELEGRAM_BOT_TOKEN en Vercel")
    return Bot(token=TG_TOKEN)

@app.get("/")
async def root():
    """Healthcheck. Si esto falla, te dice qué variable falta."""
    try:
        alpaca = get_alpaca()
        account = alpaca.get_account()
        return {
            "status": "Maestro AI Online",
            "paper": ALPACA_PAPER,
            "cash": float(account.cash),
            "equity": float(account.equity)
        }
    except Exception as e:
        logger.error(f"Error en root: {e}")
        return {"status": "Error", "detail": str(e)}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    try:
        data = await req.json()
        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = str(message.get("chat", {}).get("id", ""))

        if not TG_CHAT:
            return {"ok": True}
            
        if chat_id != TG_CHAT:
            logger.warning(f"Chat no autorizado: {chat_id}")
            return {"ok": True}

        bot = get_bot()
        alpaca = get_alpaca()

        if text == "/start":
            await bot.send_message(chat_id=TG_CHAT, text="👋 Maestro_Trading_AI listo. Usa /help")
        
        elif text == "/balance":
            account = alpaca.get_account()
            msg = f"💰 Saldo Paper: ${float(account.cash):,.2f}\n📊 Equity: ${float(account.equity):,.2f}"
            await bot.send_message(chat_id=TG_CHAT, text=msg)

        elif text == "/help":
            ayuda = "Comandos:\n/balance - Ver saldo\n/status - Estado\n/stop - Pausa"
            await bot.send_message(chat_id=TG_CHAT, text=ayuda)

        elif text == "/status":
            modo = "PAPER" if ALPACA_PAPER else "REAL ⚠️"
            await bot.send_message(chat_id=TG_CHAT, text=f"✅ Bot Online\nModo: {modo}")

        elif text == "/stop":
            await bot.send_message(chat_id=TG_CHAT, text="🛑 Bot pausado por orden del Director.")

        return {"ok": True}

    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        # Si el bot no se puede crear, no intentamos enviar mensaje
        try:
            bot = get_bot()
            await bot.send_message(chat_id=TG_CHAT, text=f"❌ Error: {e}")
        except:
            pass
        return {"ok": True}
