# ==============================================================================
# ARCHIVO: priority.py
# DEPARTAMENTO: 03 - NEXUS (Trading)
# SISTEMA: MAESTRO-NEXUS
# ROL: Gestor de Prioridades
# MISIÓN: Determinar el orden de ejecución de tareas de trading concurrentes.
# DEBERES: Cumplir con la Constitución, no hardcodear credenciales, registrar errores.
# PROHIBICIONES: Violar las reglas transversales del Manifiesto de Roles.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

# ==============================================================================
# ARCHIVO: priority.py
# MODULO: trading
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Calcular y gestionar la prioridad de activos en la watchlist 
#            usando Redis Sorted Sets para optimizar el análisis del Scheduler.
# ULTIMA MODIFICACION: 2026-07-29
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# ==============================================================================
# [MOD-2026-07-29] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Fase 12.2 - Evolucionar el scheduler de revisión secuencial a revisión por prioridad.
# REF: Optimización de recursos y enfoque en oportunidades de alto valor.

import logging

logger = logging.getLogger(__name__)

def calcular_score_prioridad(ticker: str, datos_mercado: dict = None) -> float:
    """
    Calcula un score de prioridad para un ticker.
    Score más alto = Mayor prioridad de análisis.
    Fórmula base: (Volatilidad * 0.6) + (Factor_Tiempo * 0.4)
    """
    score = 50.0 # Score base neutro
    
    if datos_mercado:
        # Si tenemos datos reales, ajustamos por volatilidad (ejemplo simplificado)
        volumen = datos_mercado.get('v', 0)
        if volumen > 1000000: # Umbral de volumen alto
            score += 30.0
            
    # En el futuro, se puede integrar con datos de VIX o distancia a soportes
    return score

async def actualizar_prioridad_en_redis(redis_client, ticker: str, score: float):
    """Actualiza o inserta el ticker en el Sorted Set de prioridades."""
    try:
        key = "watchlist:prioridad"
        # ZADD actualiza el score si el miembro ya existe
        redis_client.zadd(key, {ticker: score})
        logger.info(f"📊 Prioridad actualizada: {ticker} con score {score}")
    except Exception as e:
        logger.error(f"❌ Error actualizando prioridad en Redis: {e}")

async def obtener_activo_prioritario(redis_client) -> str:
    """Obtiene y extrae (ZPOPMAX) el activo con mayor prioridad."""
    try:
        key = "watchlist:prioridad"
        # ZPOPMAX devuelve una lista de tuplas: [(b'TICKER', score), ...]
        resultado = redis_client.zpopmax(key, count=1)
        if resultado:
            ticker_bytes, score = resultado[0]
            ticker = ticker_bytes.decode() if isinstance(ticker_bytes, bytes) else ticker_bytes
            logger.info(f"🎯 Activo prioritario seleccionado: {ticker} (Score: {score})")
            return ticker
        return None
    except Exception as e:
        logger.error(f"❌ Error obteniendo activo prioritario: {e}")
        return None
