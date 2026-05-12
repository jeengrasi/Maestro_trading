import os

# Este archivo centraliza tus variables de Vercel para que el bot las entienda
class Config:
    # Claves de Alpaca
    ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
    ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
    ALPACA_PAPER = os.getenv("ALPACA_PAPER", "true").lower() == "true"

    # Configuración de Riesgo (Convertimos el texto de Vercel a números)
    RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "0.01"))
    MAX_TRADES_PER_DAY = int(os.getenv("MAX_TRADES_PER_DAY", "3"))
    MAX_VIX = float(os.getenv("MAX_VIX", "20.0"))

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    # Redis (Upstash)
    REDIS_URL = os.getenv("REDIS_URL")
