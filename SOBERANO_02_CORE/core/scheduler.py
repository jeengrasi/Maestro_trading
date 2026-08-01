#!/usr/bin/env python3
# ==============================================================================
# ARCHIVO: scheduler.py
# DEPARTAMENTO: 02 - CORE (Ejecución)
# SISTEMA: MAESTRO-NEXUS
# ROL: Planificador de Tareas (El Despertador Autónomo)
# MISIÓN: Ejecutar ciclos de trading de forma periódica, verificando previamente
#         el estado del Circuit Breaker y las condiciones de mercado.
# DEBERES: Cumplir con la Constitución, no hardcodear credenciales, registrar 
#          errores, garantizar ejecuciones cíclicas sin bloqueo de memoria.
# PROHIBICIONES: Violar las reglas transversales del Manifiesto de Roles, 
#                ejecutar lógica de trading directa (delega en TradingEngine).
# ULTIMA MODIFICACION: 2026-08-01
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01, Mesa Técnica
# REFERENCIA: Constitución v7.1 (Art. 14), Fase 1.1 - Consenso Mesa
# ==============================================================================

import os
import sys
import logging
from datetime import datetime
from upstash_redis import Redis

# Agregar ruta raíz al path para importaciones correctas en Railway/Vercel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SOBERANO_03_NEXUS.config import Config
from SOBERANO_03_NEXUS.trading.engine import TradingEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    logger.info("🌅 Despertando: Inicio del ciclo programado de Maestro-Nexus.")
    
    try:
        # 1. Inicializar dependencias
        config = Config()
        redis_client = Redis(url=config.UPSTASH_REDIS_REST_URL, token=config.UPSTASH_REDIS_REST_TOKEN)
        
        # 2. Verificación de Seguridad Primaria: Circuit Breaker
        cb_state = redis_client.get("circuit_breaker:active")
        if cb_state and cb_state.decode() == "true":
            logger.warning("🛑 CIRCUIT BREAKER ACTIVO. El ciclo de trading se aborta por seguridad.")
            logger.info("💡 Para reactivar, el Director debe ejecutar el comando de autorización o esperar el TTL.")
            return {"status": "abortado", "razon": "Circuit Breaker activo"}
        
        # 3. Verificación de Autorización Temporal (Doble candado)
        # Nota: En producción, esto se activa vía comando de Telegram o variable de entorno persistente
        # Para Fase 1.1, si no está activo, se registra y se sale elegantemente (Fail-Closed)
        temp_auth = redis_client.get("AUTO_EJECUCION_TEMP")
        auth_str = temp_auth.decode() if isinstance(temp_auth, bytes) else str(temp_auth) if temp_auth else ""
        
        if auth_str.lower() != "true":
            logger.info("⏸️ Modo Sombra inactivo (AUTO_EJECUCION_TEMP != true). Ciclo en espera.")
            return {"status": "espera", "razon": "Autorización temporal no activa"}
        
        # 4. Ejecutar el Ciclo de Trading (Delegación al Ejecutor Blindado)
        logger.info("✅ Permisos verificados. Iniciando TradingEngine...")
        engine = TradingEngine(redis_client)
        
        # Watchlist oficial Fase 1.1
        watchlist_fase_1 = ["AAPL", "MSFT", "GOOGL", "SPY", "GLD"]
        
        # Ejecutar ciclo (confianza IA default 85% para Fase 1.1)
        resultado = engine.ejecutar_ciclo_trading(watchlist=watchlist_fase_1, confianza_ia_default=85.0)
        
        logger.info(f"🏁 Ciclo completado. Estado: {resultado['status']}")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ FALLO CRÍTICO EN SCHEDULER: {e}")
        # En caso de fallo crítico, activamos circuit breaker por 1 hora como medida de protección (Fail-Closed)
        try:
            redis_client.set("circuit_breaker:active", "true", ex=3600)
            logger.warning("🛡️ Circuit Breaker activado automáticamente por fallo crítico.")
        except:
            pass
        return {"status": "error", "razon": str(e)[:100]}

if __name__ == "__main__":
    main()
