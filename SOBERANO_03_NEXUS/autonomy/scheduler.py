# ==============================================================================
# ARCHIVO: scheduler.py
# DEPARTAMENTO: 03 - NEXUS (Autonomía)
# SISTEMA: MAESTRO-NEXUS
# ROL: Programador de Tareas
# MISIÓN: Ejecutar tareas autónomas periódicas (ej: análisis de mercado).
# DEBERES: Cumplir con la Constitución, no hardcodear credenciales, registrar errores.
# PROHIBICIONES: Violar las reglas transversales del Manifiesto de Roles.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

from SOBERANO_03_NEXUS.trading.priority import obtener_activo_prioritario, actualizar_prioridad_en_redis, calcular_score_prioridad
# ==============================================================================
# ARCHIVO: scheduler.py
# MODULO: autonomy
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Scheduler Autónomo - Ejecuta análisis de mercado periódicamente
#            y notifica al Director solo cuando hay oportunidades reales.
# ULTIMA MODIFICACION: 2026-07-28
# AUTOR: Gerente (Qwen) | VALIDADO POR: Mesa Tecnica (Meta, Gemini)
# ==============================================================================
# [MOD-2026-07-28] [AUTO: Qwen] [VALIDADOR: META, GEMINI, JEISSON_01]
# MOTIVO: Implementar proactividad real (Fase 7.2).
# REF: Hoja de Ruta Fase 6-7, Decision Gerencial

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Lista de activos a monitorear (puede expandirse via Redis)
DEFAULT_WATCHLIST = ["AAPL", "TSLA", "NVDA", "SPY", "QQQ"]

async def ejecutar_analisis_periodico(redis_client, send_telegram_func, chat_id: int) -> dict:
    """
    Ejecuta análisis autónomo sobre la watchlist predefinida.
    Solo notifica al Director si detecta oportunidades de COMPRA o si el freno se activa.
    
    Args:
        redis_client: Cliente Redis para memoria y configuración
        send_telegram_func: Función para enviar mensajes a Telegram
        chat_id: ID del chat de Telegram del Director
    
    Returns:
        dict con resumen de la ejecución
    """
    logger.info("🤖 [SCHEDULER] Iniciando análisis periódico...")
    await send_telegram_func("🤖 *[SCHEDULER AUTÓNOMO]* Iniciando escaneo de mercado...", chat_id=chat_id)
    
    # 1. Verificar Freno de Emergencia
    cb_active = redis_client.get("circuit_breaker:active")
    if cb_active and cb_active.decode() == "true":
        await send_telegram_func("🔴 *[SCHEDULER]* Frenos activos. Escaneo suspendido.", chat_id=chat_id)
        return {"status": "blocked", "reason": "circuit_breaker", "analizados": 0}
    
    # 2. Obtener watchlist (de Redis si existe, sino usar default)
    watchlist_raw = redis_client.get("trading:watchlist")
    if watchlist_raw:
        watchlist = watchlist_raw.decode().split(",")
    else:
        watchlist = DEFAULT_WATCHLIST
        # Guardar default en Redis para futura personalización
        redis_client.set("trading:watchlist", ",".join(DEFAULT_WATCHLIST))
    
    # 3. Importar el motor de trading
    from SOBERANO_03_NEXUS.trading.engine import analizar_y_ejecutar_sombra
    
    resultados = []
    oportunidades = []
    
    # 4. Analizar cada activo de la watchlist
        # FASE 12.2: Obtener solo el activo de mayor prioridad en lugar de iterar toda la lista
    ticker = await obtener_activo_prioritario(redis_client)
    if not ticker:
        logger.info("📭 No hay activos en la cola de prioridad para analizar.")
        return {"status": "empty_queue"}

    logger.info(f"🎯 Analizando activo prioritario: {ticker}")
    # Simulamos la obtención de datos para el score (en producción vendría de Alpaca)
    datos_mock = {'v': 1500000} 
    score = calcular_score_prioridad(ticker, datos_mock)
    # Si no se ejecuta, se devuelve a la cola con su score
    await actualizar_prioridad_en_redis(redis_client, ticker, score)

    # Lista temporal para el análisis (contiene solo 1 activo prioritario)
    watchlist_prioritaria = [ticker]
    for ticker in watchlist_prioritaria:
        ticker = ticker.strip().upper()
        try:
            resultado = await analizar_y_ejecutar_sombra(ticker, redis_client, send_telegram_func, chat_id)
            resultados.append(resultado)
            
            if resultado.get("es_compra") and resultado.get("status") == "executed":
                oportunidades.append(f"✅ {ticker} - COMPRA EJECUTADA")
            elif resultado.get("es_compra") and resultado.get("status") == "analyzed":
                oportunidades.append(f"🟡 {ticker} - SEÑAL DE COMPRA (AUTO_EJECUCION=OFF)")
                
        except Exception as e:
            logger.error(f"Error analizando {ticker}: {e}")
            resultados.append({"ticker": ticker, "status": "error", "reason": str(e)[:50]})
    
    # 5. Registrar ejecución en bitácora de Redis
    redis_client.lpush("memoria:scheduler:ejecuciones", 
                       f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Analizados: {len(watchlist)} | Oportunidades: {len(oportunidades)}")
    redis_client.ltrim("memoria:scheduler:ejecuciones", 0, 49)
    
    # 6. Resumen final
    resumen = {
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
        "analizados": len(watchlist),
        "oportunidades": len(oportunidades),
        "detalles": oportunidades
    }
    
    logger.info(f"✅ [SCHEDULER] Escaneo completado: {len(watchlist)} analizados, {len(oportunidades)} oportunidades")
    return resumen
