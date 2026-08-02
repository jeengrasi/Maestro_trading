import os
import logging
from fastapi import FastAPI
from SOBERANO_03_NEXUS.telegram.webhook import router as telegram_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Maestro-Nexus API")

# Incluir únicamente el router de Telegram
app.include_router(telegram_router)

@app.get("/")
async def root():
    return {"status": "active", "system": "Maestro-Nexus", "version": "v7.1"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
