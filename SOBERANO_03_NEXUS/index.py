import os
import logging
from fastapi import FastAPI
from SOBERANO_03_NEXUS.telegram.webhook import router as telegram_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Maestro-Nexus API")

# Incluir el router de Telegram
app.include_router(telegram_router)

@app.get("/")
async def root():
    return {"status": "active", "system": "Maestro-Nexus", "version": "v7.1"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/debug-env")
async def debug_env():
    # Muestra el estado real de las variables de entorno en el servidor
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("DIRECTOR_CHAT_ID", "NO_CONFIGURADO")
    
    return {
        "sistema": "Maestro-Nexus v7.1",
        "auditoria_variables_en_vivo": {
            "TELEGRAM_BOT_TOKEN_existe": bool(token),
            "TELEGRAM_BOT_TOKEN_longitud": len(token),
            "TELEGRAM_BOT_TOKEN_inicio": token[:5] + "..." if token else "VACIO",
            "DIRECTOR_CHAT_ID_valor": chat_id,
            "ALPACA_API_KEY_existe": bool(os.getenv("ALPACA_API_KEY")),
            "UPSTASH_REDIS_existe": bool(os.getenv("UPSTASH_REDIS_REST_URL")),
            "PUERTO_ACTUAL": os.getenv("PORT", "8080")
        },
        "instruccion": "Si 'DIRECTOR_CHAT_ID_valor' es 'NO_CONFIGURADO' o un numero que no es el suyo, ese es el problema."
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
