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



@app.get("/debug-alpaca")
async def debug_alpaca():
    import httpx
    import json
    
    api_key = os.getenv("ALPACA_API_KEY", "")
    secret_key = os.getenv("ALPACA_SECRET_KEY", "")
    
    resultado = {
        "servidor": "Railway (En vivo)",
        "variables_leidas": {
            "API_KEY_longitud": len(api_key),
            "API_KEY_inicio": api_key[:4] + "..." if len(api_key) > 4 else "VACIO",
            "SECRET_KEY_longitud": len(secret_key),
        },
        "prueba_http_directa": "Pendiente..."
    }
    
    if not api_key or not secret_key:
        resultado["prueba_http_directa"] = "FALLIDO: Variables vacías en Railway."
        return resultado
        
    try:
        # Petición HTTP cruda directa a Paper Trading, sin librerías intermediarias
        url = "https://paper-api.alpaca.markets/v2/account"
        headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            
            resultado["prueba_http_directa"] = {
                "status_code": response.status_code,
                "respuesta_de_alpaca": response.text
            }
            
    except Exception as e:
        resultado["prueba_http_directa"] = f"ERROR DE RED: {str(e)}"
        
    return resultado

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
