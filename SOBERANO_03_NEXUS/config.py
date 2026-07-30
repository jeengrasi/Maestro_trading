# ==============================================================================
# ARCHIVO: config.py
# DEPARTAMENTO: 03 - NEXUS (Raíz)
# SISTEMA: MAESTRO-NEXUS
# ROL: Gestor de Configuración
# MISIÓN: Cargar y validar variables de entorno y configuraciones globales.
# DEBERES: Cumplir con la Constitución, no hardcodear credenciales, registrar errores.
# PROHIBICIONES: Violar las reglas transversales del Manifiesto de Roles.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

import os

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6444278889")
    ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
    ALPACA_PAPER = os.getenv("ALPACA_PAPER", "true").strip().lower() == "true"
    MAX_VIX = float(os.getenv("MAX_VIX", "20.0"))
    RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "0.01"))
    AUTO_EJECUCION = os.getenv("AUTO_EJECUCION", "false").lower() == "true"
    UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL", "")
    UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")


# ==============================================================================
# [MOD-2026-07-29] FASE 12.1: Soporte para AUTO_EJECUCION_TEMP en Redis
# PROPÓSITO: Permitir activación temporal de ejecución autónoma (TTL 1h)
# ==============================================================================
def get_auto_ejecucion_state(redis_client=None) -> bool:
    """
    Verifica si la ejecución autónoma está permitida.
    Prioridad 1: Clave temporal en Redis (AUTO_EJECUCION_TEMP con TTL).
    Prioridad 2: Variable de entorno del sistema.
    """
    if redis_client:
        try:
            temp_state = redis_client.get("AUTO_EJECUCION_TEMP")
            if temp_state:
                val = temp_state.decode() if isinstance(temp_state, bytes) else str(temp_state)
                if val.lower() == "true":
                    return True
        except Exception:
            pass # Fallback a env var si falla Redis
    
    return os.getenv("AUTO_EJECUCION", "false").lower() == "true"
