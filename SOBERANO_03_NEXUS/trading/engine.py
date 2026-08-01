# ==============================================================================
# ARCHIVO: engine.py
# MODULO: trading
# DEPARTAMENTO: 03 - NEXUS (Trading)
# SISTEMA: MAESTRO-NEXUS
# ROL: El Ejecutor Blindado
# MISIÓN: Orquestar el análisis, riesgo y ejecución de Bracket Orders en Alpaca
#         solo con autorización temporal válida.
# DEBERES: Verificar AUTO_EJECUCION_TEMP, integrar Risk Manager, Strategy Engine 
#          y Position Sizer. Delegar Stop-Loss al bróker (Fail-Closed).
# PROHIBICIONES: Enviar mensajes a Telegram directamente, manejar memoria 
#                conversacional, ejecutar sin autorización válida.
# ULTIMA MODIFICACION: 2026-08-01
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01, Mesa Técnica
# REFERENCIA: Constitución v7.1 (Art. 14), Fase 1.1 - Consenso Mesa
# ==============================================================================

import os
import logging
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass
from SOBERANO_03_NEXUS.config import Config
from SOBERANO_03_NEXUS.trading.risk_manager import RiskManager
from SOBERANO_03_NEXUS.trading.strategy_engine import StrategyEngine
from SOBERANO_03_NEXUS.trading.position_sizer import PositionSizer

logger = logging.getLogger(__name__)

class TradingEngine:
    """
    El Ejecutor Blindado del sistema.
    Orquesta el análisis, riesgo y ejecución de Bracket Orders en Alpaca.
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.config = Config()
        
        # Inicializar cliente de trading de Alpaca
        self.trading_client = TradingClient(
            self.config.ALPACA_API_KEY, 
            self.config.ALPACA_SECRET_KEY, 
            paper=self.config.ALPACA_PAPER
        )
        
        # Inicializar módulos
        self.risk_manager = RiskManager(redis_client)
        self.strategy_engine = StrategyEngine()
        
        # Capital inicial de referencia (se actualiza dinámicamente)
        self.capital_inicial = 10000.0  

    def obtener_capital_disponible(self) -> float:
        """Obtiene el capital disponible (Buying Power) de la cuenta de Alpaca."""
        try:
            account = self.trading_client.get_account()
            buying_power = float(account.buying_power)
            # Actualizar capital inicial si es la primera vez o si cambió significativamente
            if self.capital_inicial == 10000.0:
                self.capital_inicial = buying_power
            return buying_power
        except Exception as e:
            logger.error(f"❌ Error obteniendo capital de Alpaca: {e}")
            return self.capital_inicial

    def ejecutar_ciclo_trading(self, watchlist: list = None, confianza_ia_default: float = 85.0):
        """
        Ejecuta el ciclo completo de trading para la watchlist.
        
        Args:
            watchlist: Lista de símbolos a analizar.
            confianza_ia_default: Confianza por defecto (85.0 = factor 1.0, riesgo 0.4%).
                                  En el futuro, esto vendrá del parliament/core.py.
        """
        if watchlist is None:
            watchlist = ["AAPL", "MSFT", "GOOGL", "SPY", "GLD"]
            
        logger.info(f"🚀 Iniciando ciclo de trading. Watchlist: {watchlist}")
        
        # 1. Verificar autorización temporal
        temp_auth = self.redis.get("AUTO_EJECUCION_TEMP")
        if not temp_auth or (isinstance(temp_auth, bytes) and temp_auth.decode().lower() != "true"):
            logger.info("⏸️ AUTO_EJECUCION_TEMP no está activo. Ciclo de trading abortado.")
            return {"status": "abortado", "razon": "AUTO_EJECUCION_TEMP inactivo"}
            
        # 2. Obtener capital actual
        capital_actual = self.obtener_capital_disponible()
        logger.info(f"💰 Capital disponible: ${capital_actual:.2f}")
        
        resultados = []
        
        for symbol in watchlist:
            try:
                logger.info(f"🔍 Analizando {symbol}...")
                
                # 3. Análisis Técnico
                analisis = self.strategy_engine.calcular_confluencia(symbol)
                
                if analisis["señal"] != "COMPRA":
                    logger.info(f"⏸️ {symbol}: {analisis['razon']}")
                    resultados.append({"symbol": symbol, "accion": "ESPERA", "razon": analisis["razon"]})
                    continue
                
                # 4. Evaluación de Riesgo (Risk Manager)
                precio_actual = analisis["precio_actual"]
                atr_14 = analisis["atr_14"]
                
                # Calcular Stop Loss dinámico (2x ATR)
                stop_loss = precio_actual - (2 * atr_14) if atr_14 > 0 else precio_actual * 0.95
                
                evaluacion_riesgo = self.risk_manager.evaluar_operacion(
                    symbol=symbol,
                    capital_actual=capital_actual,
                    capital_inicial=self.capital_inicial,
                    confianza_ia=confianza_ia_default
                )
                
                if not evaluacion_riesgo["autorizado"]:
                    logger.warning(f"🛑 {symbol}: Operación bloqueada por Risk Manager. Razón: {evaluacion_riesgo['razon']}")
                    resultados.append({"symbol": symbol, "accion": "BLOQUEADO", "razon": evaluacion_riesgo["razon"]})
                    continue
                
                # 5. Cálculo de Posición
                factor_ia = evaluacion_riesgo["factor_riesgo"]
                position_sizer = PositionSizer(capital_actual)
                tamaño_posicion = position_sizer.calcular_tamaño_posicion(
                    precio_entrada=precio_actual,
                    stop_loss=stop_loss,
                    factor_ia=factor_ia
                )
                
                if tamaño_posicion["acciones"] <= 0:
                    logger.warning(f"⚠️ {symbol}: Posición inválida. Razón: {tamaño_posicion['razon']}")
                    resultados.append({"symbol": symbol, "accion": "RECHAZADO", "razon": tamaño_posicion["razon"]})
                    continue
                
                # 6. Ejecución de Bracket Order (Fail-Closed)
                logger.info(f"✅ {symbol}: Ejecutando Bracket Order. Acciones: {tamaño_posicion['acciones']}")
                
                # Calcular Take Profit (Relación Riesgo/Beneficio 1:2)
                riesgo_por_accion = precio_actual - stop_loss
                take_profit = precio_actual + (2 * riesgo_por_accion)
                
                # Crear orden de mercado con legs de Stop Loss y Take Profit
                order_data = {
                    "symbol": symbol,
                    "qty": tamaño_posicion["acciones"],
                    "side": OrderSide.BUY,
                    "type": "market",
                    "time_in_force": TimeInForce.DAY,
                    "order_class": OrderClass.BRACKET,
                    "take_profit": {
                        "limit_price": round(take_profit, 2)
                    },
                    "stop_loss": {
                        "stop_price": round(stop_loss, 2)
                    }
                }
                
                # Ejecutar orden en Alpaca
                orden = self.trading_client.submit_order(order_data=order_data)
                
                logger.info(f"🎯 {symbol}: Orden ejecutada exitosamente. Order ID: {orden.id}")
                
                resultados.append({
                    "symbol": symbol,
                    "accion": "COMPRADO",
                    "orden_id": orden.id,
                    "cantidad": tamaño_posicion["acciones"],
                    "precio_entrada": round(precio_actual, 2),
                    "stop_loss": round(stop_loss, 2),
                    "take_profit": round(take_profit, 2),
                    "riesgo_pct": tamaño_posicion["riesgo_pct"]
                })
                
            except Exception as e:
                logger.error(f"❌ Error procesando {symbol}: {e}")
                resultados.append({"symbol": symbol, "accion": "ERROR", "razon": str(e)[:100]})
                
        return {"status": "completado", "resultados": resultados}

# ==============================================================================
# REGISTRO DE CAMBIOS (CHANGELOG VIVO)
# ==============================================================================
# [2026-08-01] [Qwen]: Integración de RiskManager, StrategyEngine y PositionSizer. 
#                       Ejecución de Bracket Orders con delegación de SL al bróker.
# ==============================================================================
