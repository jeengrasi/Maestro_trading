from fastapi import FastAPI, HTTPException
from alpaca.trading.client import TradingClient
import os
import logging

# Configuración de logs para ver en Vercel Dashboard
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def get_trading_client():
    # Leemos las variables DENTRO de la función, no fuera.
    key = os.environ.get("ALPACA_API_KEY")
    secret = os.environ.get("ALPACA_SECRET_KEY")
    paper = os.environ.get("ALPACA_PAPER", "true").lower() == "true"
    
    if not key or not secret:
        logger.error(f"Error de ENV: KEY presente: {bool(key)}, SECRET presente: {bool(secret)}")
        raise ValueError("Faltan credenciales de Alpaca en os.environ")
    
    return TradingClient(key, secret, paper=paper), paper

@app.get("/")
async def root():
    try:
        alpaca, is_paper = get_trading_client()
        account = alpaca.get_account()
        return {
            "status": "Maestro AI Online",
            "mode": "Paper Trading" if is_paper else "Live",
            "cash": float(account.cash),
            "currency": account.currency
        }
    except Exception as e:
        logger.error(f"Fallo en root: {str(e)}")
        return {"status": "Error", "detail": str(e)}

# ENDPOINT DE PRUEBA: Para ver qué variables detecta Vercel (borrar después de probar)
@app.get("/debug-env")
async def debug_env():
    # Solo mostramos las llaves (keys), NO los valores por seguridad
    return {
        "keys_detected": list(os.environ.keys()),
        "python_version": os.sys.version,
        "api_key_found": "ALPACA_API_KEY" in os.environ
    }
