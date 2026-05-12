from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
async def root():
    # Esto NO muestra los valores, solo los nombres de variables que existen
    env_keys = [key for key in os.environ.keys() if 'ALPACA' in key or 'TELEGRAM' in key]
    return {
        "status": "Debug Mode",
        "variables_encontradas": env_keys,
        "total_vars": len(os.environ)
    }
