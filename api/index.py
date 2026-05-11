from fastapi import FastAPI, Request
from alpaca.trading.client import TradingClient
from telegram import Bot
import os

app = FastAPI()

ALPACA_KEY = os.environ.get("ALPACA_API_KEY")
ALPACA_SECRET = os.environ.get("ALPACA_SECRET_KEY")
ALPACA_PAPER = os.environ.get("ALPACA_PAPER", "true").lower() == "true"
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID")

alpaca = TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=ALPACA_PAPER)
bot = Bot(token=TG_TOKEN)

@app.on_event("startup")
async def startup_event():
    try:
        account = alpaca.get_account()
        saldo = float(account.cash)
        mensaje = f"🚀 Maestro_Trading_AI Online | Paper Trading: ACTIVO | Saldo: ${saldo:,.2f}"
        await bot.send_message(chat_id=TG_CHAT, text=mensaje)
    except Exception as e:
        await bot.send_message(chat_id=TG_CHAT, text=f"⚠️ Error al iniciar: {e}")

@app.get("/")
async def root():
    return {"status": "Maestro AI Online", "paper": ALPACA_PAPER}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    if "message" in data:
        text = data["message"].get("text", "")
        if text == "/start" or text == "/balance":
            account = alpaca.get_account()
            await bot.send_message(chat_id=TG_CHAT, text=f"Saldo Paper: ${float(account.cash):,.2f}")
        elif text == "/stop":
            await bot.send_message(chat_id=TG_CHAT, text="🛑 Bot pausado por orden del Director.")
    return {"ok": True}
