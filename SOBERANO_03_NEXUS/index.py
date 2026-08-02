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


@app.get("/debug-alpaca-dual")
async def debug_alpaca_dual():
    import httpx
    
    api_key = os.getenv("ALPACA_API_KEY", "").strip()
    secret_key = os.getenv("ALPACA_SECRET_KEY", "").strip()
    
    resultado = {
        "servidor": "Railway (En vivo)",
        "variables_saneadas": {
            "API_KEY_longitud": len(api_key),
            "API_KEY_repr": repr(api_key[:10]) + "..." if api_key else "VACIO",
            "SECRET_KEY_longitud": len(secret_key),
        },
        "prueba_paper": "Pendiente...",
        "prueba_live": "Pendiente...",
        "diagnostico_final": "Pendiente..."
    }
    
    if not api_key or not secret_key:
        resultado["diagnostico_final"] = "FALLIDO: Variables vacías"
        return resultado
    
    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key
    }
    
    # Probar Paper Trading
    try:
        async with httpx.AsyncClient() as client:
            resp_paper = await client.get("https://paper-api.alpaca.markets/v2/account", headers=headers, timeout=10.0)
            resultado["prueba_paper"] = {
                "status_code": resp_paper.status_code,
                "respuesta": resp_paper.text[:200]
            }
    except Exception as e:
        resultado["prueba_paper"] = f"ERROR: {str(e)}"
    
    # Probar Live Trading
    try:
        async with httpx.AsyncClient() as client:
            resp_live = await client.get("https://api.alpaca.markets/v2/account", headers=headers, timeout=10.0)
            resultado["prueba_live"] = {
                "status_code": resp_live.status_code,
                "respuesta": resp_live.text[:200]
            }
    except Exception as e:
        resultado["prueba_live"] = f"ERROR: {str(e)}"
    
    # Diagnóstico final
    paper_ok = isinstance(resultado["prueba_paper"], dict) and resultado["prueba_paper"].get("status_code") == 200
    live_ok = isinstance(resultado["prueba_live"], dict) and resultado["prueba_live"].get("status_code") == 200
    
    if paper_ok and not live_ok:
        resultado["diagnostico_final"] = "✅ CLAVES DE PAPER TRADING - Use endpoint paper-api"
    elif live_ok and not paper_ok:
        resultado["diagnostico_final"] = "⚠️ CLAVES DE LIVE TRADING - Las claves son de cuenta real, no paper"
    elif paper_ok and live_ok:
        resultado["diagnostico_final"] = "❌ ANOMALÍA: Ambas cuentas aceptan las claves"
    else:
        resultado["diagnostico_final"] = "❌ CLAVES INVÁLIDAS: Ninguna cuenta acepta estas credenciales"
    
    return resultado

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
