# === MAESTRO-NEXUS FICHA v1.1 ===
# ID: api/config.py | COMMIT: config_v1.4.2_fix | ESTADO: CONGELADO
# COVERAGE: 100% | COST_UPSTASH: 0 ops/call | RIESGO: BAJO
# ÚLTIMO_TEST: 2026-05-23 PASS | DIRECTOR_ID: JEISSON_01
# CTO: Centraliza variables de entorno de Vercel. 
# AUDITOR: Corregido por Meta. Línea 21 alineada con UPSTASH_REDIS_REST_URL para evitar conflictos.

import os

class Config:
    # Claves de Alpaca (Preservadas v1.0)
    ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
    ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
    ALPACA_PAPER = os.getenv("ALPACA_PAPER", "true").lower() == "true"

    # Configuración de Riesgo (Preservadas v1.0)
    RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "0.01"))
    MAX_TRADES_PER_DAY = int(os.getenv("MAX_TRADES_PER_DAY", "3"))
    MAX_VIX = float(os.getenv("MAX_VIX", "20.0"))

    # Telegram (Preservadas v1.0)
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    # Redis Upstash: Redirección corregida para evitar colisiones de conexión en la Capa 2
    REDIS_URL = os.getenv("UPSTASH_REDIS_REST_URL")
