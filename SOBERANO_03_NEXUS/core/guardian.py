#!/usr/bin/env python3
# ==============================================================================
# ARCHIVO: guardian.py
# DEPARTAMENTO: 03 - NEXUS (Núcleo)
# SISTEMA: MAESTRO-NEXUS
# ROL: El Guardián de Integridad (Hard-Fail)
# MISIÓN: Validar condiciones vitales antes de permitir el arranque del sistema.
# DEBERES: Cumplir con el Art. X.2 del Protocolo de Hierro.
# ==============================================================================
import os
import sys
import logging

logger = logging.getLogger(__name__)

CRITICAL_VARS = [
    "ALPACA_API_KEY",
    "ALPACA_SECRET_KEY",
    "TELEGRAM_BOT_TOKEN",
    "DIRECTOR_CHAT_ID",
    "UPSTASH_REDIS_REST_URL",
    "UPSTASH_REDIS_REST_TOKEN"
]

def verify_startup_requirements():
    """
    Verifica que todas las variables críticas estén presentes y no estén vacías.
    Si falta alguna, lanza una excepción que detiene el arranque de la aplicación (Hard-Fail).
    """
    logger.info("🛡️ [GUARDIÁN] Iniciando verificación de requisitos de arranque...")
    
    missing_vars = []
    empty_vars = []
    
    for var in CRITICAL_VARS:
        value = os.getenv(var)
        if value is None:
            missing_vars.append(var)
        elif not value.strip():
            empty_vars.append(var)
            
    if missing_vars or empty_vars:
        error_msg = "🚨 [GUARDIÁN] FALLO CRÍTICO DE ARRANQUE (HARD-FAIL):\n"
        if missing_vars:
            error_msg += f"   - Variables FALTANTES: {', '.join(missing_vars)}\n"
        if empty_vars:
            error_msg += f"   - Variables VACÍAS: {', '.join(empty_vars)}\n"
        error_msg += "   El sistema se niega a operar a ciegas. Configure las variables de entorno y reinicie."
        
        logger.error(error_msg)
        raise ValueError(error_msg)
        
    logger.info("✅ [GUARDIÁN] Verificación completada. Todas las variables críticas están presentes y válidas.")
    return True
