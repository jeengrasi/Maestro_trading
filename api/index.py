from fastapi import FastAPI, Request
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import os
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

ALPACA_KEY = os.environ.get("ALPACA_API_KEY")
ALPACA_SECRET = os.environ.get("ALPACA_SECRET_KEY")
ALPACA_PAPER = os.environ.get("ALPACA_PAPER", "true").lower() == "true"
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID")

def get_alpaca():
    if not ALPACA_KEY or not ALPACA_SECRET:
        raise ValueError("Faltan ALPACA_API_KEY o ALPACA_SECRET_KEY")
    return TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=ALPACA_PAPER)

async def send_telegram(text: str):
    if not TG_TOKEN or not TG_CHAT:
        logger.error("Faltan TG_TOKEN o TG_CHAT")
        return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": TG_CHAT, "text": text, "parse_mode": "Markdown"})

@app.get("/")
async def root():
    try:
        alpaca = get_alpaca()
        account = alpaca.get_account()
        return {"status":"Maestro AI Online","mode":"Paper Trading" if ALPACA_PAPER else "Live","cash":float(account.cash),"currency":"USD"}
    except Exception as e:
        logger.error(f"Error en root: {e}")
        return {"status":"Error","detail":str(e)}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    try:
        data = await req.json()
        logger.info(f"Update recibido: {data}")
        
        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = str(message.get("chat", {}).get("id", ""))
        
        if chat_id != TG_CHAT:
            logger.warning(f"Chat ID no autorizado: {chat_id}")
            return {"ok": True}
        
        if text == "/start":
            await send_telegram("👋 *Maestro_Trading_AI listo.*\n\nComandos:\n/balance - Ver saldo\n/status - Estado del bot\n/help - Ayuda")
        
        elif text == "/balance":
            alpaca = get_alpaca()
            account = alpaca.get_account()
            msg = f"💰 *Saldo Paper:* ${float(account.cash):,.2f} USD\n📊 *Equity:* ${float(account.equity):,.2f}\n🟢 *Modo:* {'Paper Trading' if ALPACA_PAPER else 'Live'}"
            await send_telegram(msg)
            
        elif text == "/status":
            await send_telegram("✅ *Bot Online*\n🟢 Conectado a Alpaca\n🟢 Webhook activo")
            
        elif text == "/help":
            await send_telegram("Comandos disponibles:\n/balance - Ver tu saldo\n/status - Estado del sistema")
            
        else:
            await send_telegram("Comando no reconocido. Usa /help")
            
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        await send_telegram(f"❌ Error: {str(e)}")
    
    return {"ok": True}
