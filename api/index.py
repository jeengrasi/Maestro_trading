from fastapi import FastAPI, Request
from alpaca.trading.client import TradingClient
import os
import asyncio
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

app = FastAPI()

# --- CONFIGURACIÓN ---
def get_env():
    return {
        "key": os.environ.get("ALPACA_API_KEY"),
        "secret": os.environ.get("ALPACA_SECRET_KEY"),
        "paper": os.environ.get("ALPACA_PAPER", "true").lower() == "true",
        "token": os.environ.get("TELEGRAM_BOT_TOKEN"),
        "chat_id": os.environ.get("TELEGRAM_CHAT_ID")
    }

# --- LÓGICA DE ALPACA ---
def get_balance():
    env = get_env()
    client = TradingClient(env["key"], env["secret"], paper=env["paper"])
    account = client.get_account()
    return float(account.cash)

# --- ENDPOINTS WEB ---
@app.get("/")
async def root():
    env = get_env()
    try:
        cash = get_balance()
        # Intentar enviar mensaje de prueba al iniciar
        if env["token"] and env["chat_id"]:
            bot = telegram.Bot(token=env["token"])
            await bot.send_message(chat_id=env["chat_id"], text=f"✅ Maestro AI Conectado\n💰 Saldo inicial: ${cash:,.2f}")
        return {"status": "Online", "cash": cash}
    except Exception as e:
        return {"status": "Error", "detail": str(e)}

# --- WEBHOOK PARA TELEGRAM ---
@app.post("/webhook")
async def telegram_webhook(request: Request):
    env = get_env()
    bot = telegram.Bot(token=env["token"])
    data = await request.json()
    update = Update.de_json(data, bot)
    
    if update.message and update.message.text == "/status":
        cash = get_balance()
        await bot.send_message(
            chat_id=env["chat_id"], 
            text=f"📊 *Estado Actual*\n\n💰 Disponible: ${cash:,.2f}\n🚀 Modo: {'Paper' if env['paper'] else 'Real'}",
            parse_mode="Markdown"
        )
    return {"ok": True}
