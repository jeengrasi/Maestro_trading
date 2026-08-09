#!/usr/bin/env python3
# ==============================================================================
# ARCHIVO: index.py
# ROL: Application Factory (Orquestador puro, < 40 líneas)
# ==============================================================================
import os
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from SOBERANO_03_NEXUS.core.guardian import verify_startup_requirements
from SOBERANO_03_NEXUS.telegram.webhook import router as telegram_router
from SOBERANO_03_NEXUS.core.diagnostics import router as diagnostics_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🛡️ Iniciando validación Hard-Fail del sistema...")
    verify_startup_requirements()
    logger.info("✅ Sistema validado. Listo para operar.")
    yield
    logger.info("Apagando Maestro-Nexus de forma segura...")

app = FastAPI(title="Maestro-Nexus API", version="6.1", lifespan=lifespan)

app.include_router(telegram_router)

# ENMIENDA META 1: Debug solo si MODO_DEBUG=true (Evita fuga de info en prod)
if os.getenv("MODO_DEBUG", "false").lower() == "true":
    app.include_router(diagnostics_router)
    logger.warning("⚠️ MODO DEBUG ACTIVADO: Endpoints de diagnóstico expuestos.")

@app.get("/")
async def root():
    return {"status": "active", "system": "Maestro-Nexus", "version": "v6.1"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 Iniciando en puerto {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
