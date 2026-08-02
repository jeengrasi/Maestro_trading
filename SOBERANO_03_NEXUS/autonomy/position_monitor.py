#!/usr/bin/env python3
# ==============================================================================
# ARCHIVO: position_monitor.py
# MODULO: autonomy
# DEPARTAMENTO: 03 - NEXUS (Autonomía)
# SISTEMA: MAESTRO-NEXUS
# ROL: Monitor de Posiciones Abiertas
# MISIÓN: Verificar cada 15 minutos si las posiciones abiertas se han cerrado
#         (por Take Profit o Stop Loss) y notificar al Director.
# DEBERES: Consultar API de Alpaca, detectar cierres, calcular P&L, notificar.
# PROHIBICIONES: Ejecutar nuevas órdenes, modificar estrategias.
# ULTIMA MODIFICACION: 2026-08-01
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: Constitución v7.1 (Art. 14), Fase 1.2
# ==============================================================================

import os
import sys
import logging
from datetime import datetime
from alpaca.trading.client import TradingClient
from upstash_redis import Redis
from SOBERANO_03_NEXUS.config import Config
from SOBERANO_03_NEXUS.telegram.utils import send_telegram
from SOBERANO_03_NEXUS.telegram.formatters import format_cierre_posicion, format_resumen_diario

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class PositionMonitor:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.config = Config()
        self.trading_client = TradingClient(
            self.config.ALPACA_API_KEY,
            self.config.ALPACA_SECRET_KEY,
            paper=self.config.ALPACA_PAPER
        )
        self.chat_id = int(os.getenv("DIRECTOR_CHAT_ID", "0"))
    
    def verificar_cierres(self):
        """Verifica si las posiciones abiertas se han cerrado."""
        try:
            # Obtener posiciones actuales de Alpaca
            posiciones_actuales = self.trading_client.get_all_positions()
            symbols_actuales = {pos.symbol for pos in posiciones_actuales}
            
            # Obtener símbolos que estábamos monitoreando
            symbols_monitoreados = self.redis.smembers("posiciones:monitoreadas")
            if not symbols_monitoreados:
                logger.info("No hay posiciones monitoreadas")
                return
            
            symbols_monitoreados = {s.decode() if isinstance(s, bytes) else s for s in symbols_monitoreados}
            
            # Detectar posiciones cerradas
            symbols_cerrados = symbols_monitoreados - symbols_actuales
            
            if symbols_cerrados:
                logger.info(f"Posiciones cerradas detectadas: {symbols_cerrados}")
                
                # Para cada posición cerrada, obtener detalles y notificar
                for symbol in symbols_cerrados:
                    self._notificar_cierre(symbol)
                    
                    # Remover del conjunto de monitoreadas
                    self.redis.srem("posiciones:monitoreadas", symbol)
            
        except Exception as e:
            logger.error(f"Error verificando cierres: {e}")
    
    def _notificar_cierre(self, symbol: str):
        """Notifica el cierre de una posición."""
        try:
            # Consultar historial de órdenes para obtener detalles
            # (Simplificado - en producción se guardaría en Redis al abrir)
            mensaje = f"✅ Posición cerrada: {symbol}\nConsulte /historial para detalles."
            
            # Enviar notificación
            import asyncio
            asyncio.run(send_telegram(mensaje, chat_id=self.chat_id))
            
        except Exception as e:
            logger.error(f"Error notificando cierre de {symbol}: {e}")
    
    def actualizar_posiciones_monitoreadas(self):
        """Actualiza el conjunto de posiciones que se están monitoreando."""
        try:
            posiciones = self.trading_client.get_all_positions()
            
            # Limpiar conjunto actual
            self.redis.delete("posiciones:monitoreadas")
            
            # Agregar posiciones actuales
            for pos in posiciones:
                self.redis.sadd("posiciones:monitoreadas", pos.symbol)
            
            logger.info(f"Posiciones monitoreadas actualizadas: {len(posiciones)}")
            
        except Exception as e:
            logger.error(f"Error actualizando posiciones monitoreadas: {e}")
    
    def enviar_resumen_diario(self):
        """Envía resumen diario al cierre del mercado."""
        try:
            account = self.trading_client.get_account()
            capital_total = float(account.equity)
            pnl_diario = float(account.equity) - float(account.last_equity)
            posiciones = self.trading_client.get_all_positions()
            
            # Calcular drawdown
            drawdown_pct = 0.0
            if float(account.last_equity) > 0:
                drawdown_pct = ((float(account.last_equity) - capital_total) / float(account.last_equity)) * 100
            
            mensaje = format_resumen_diario(
                capital_total=capital_total,
                pnl_diario=pnl_diario,
                posiciones_abiertas=len(posiciones),
                drawdown_pct=drawdown_pct
            )
            
            import asyncio
            asyncio.run(send_telegram(mensaje, chat_id=self.chat_id))
            
        except Exception as e:
            logger.error(f"Error enviando resumen diario: {e}")

def main():
    """Función principal del monitor."""
    logger.info("🔍 Iniciando Position Monitor...")
    
    try:
        config = Config()
        redis_client = Redis(url=config.UPSTASH_REDIS_REST_URL, token=config.UPSTASH_REDIS_REST_TOKEN)
        monitor = PositionMonitor(redis_client)
        
        # Actualizar posiciones monitoreadas
        monitor.actualizar_posiciones_monitoreadas()
        
        # Verificar cierres
        monitor.verificar_cierres()
        
        logger.info("✅ Position Monitor completado")
        
    except Exception as e:
        logger.error(f"❌ Error en Position Monitor: {e}")

if __name__ == "__main__":
    main()
