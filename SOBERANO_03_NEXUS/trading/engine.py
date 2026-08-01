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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingEngine:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.config = Config()
        self.trading_client = TradingClient(
            self.config.ALPACA_API_KEY, 
            self.config.ALPACA_SECRET_KEY, 
            paper=self.config.ALPACA_PAPER
        )
        self.risk_manager = RiskManager(redis_client)
        self.strategy_engine = StrategyEngine()
        self.capital_inicial = 10000.0  

    def obtener_capital_disponible(self) -> float:
        try:
            account = self.trading_client.get_account()
            buying_power = float(account.buying_power)
            if self.capital_inicial == 10000.0:
                self.capital_inicial = buying_power
            return buying_power
        except Exception as e:
            logger.error(f"❌ Error obteniendo capital de Alpaca: {e}")
            return self.capital_inicial

    def ejecutar_ciclo_trading(self, watchlist: list = None, confianza_ia_default: float = 85.0):
        if watchlist is None:
            watchlist = ["AAPL", "MSFT", "GOOGL", "SPY", "GLD"]
            
        logger.info(f"🚀 Iniciando ciclo de trading. Watchlist: {watchlist}")
        
        temp_auth = self.redis.get("AUTO_EJECUCION_TEMP")
        auth_str = temp_auth.decode() if isinstance(temp_auth, bytes) else str(temp_auth) if temp_auth else ""
        
        if auth_str.lower() != "true":
            logger.info("⏸️ AUTO_EJECUCION_TEMP no está activo. Ciclo abortado.")
            return {"status": "abortado", "razon": "AUTO_EJECUCION_TEMP inactivo"}
            
        capital_actual = self.obtener_capital_disponible()
        logger.info(f"💰 Capital disponible: ${capital_actual:.2f}")
        
        resultados = []
        for symbol in watchlist:
            try:
                analisis = self.strategy_engine.calcular_confluencia(symbol)
                if analisis["señal"] != "COMPRA":
                    logger.info(f"⏸️ {symbol}: {analisis['razon']}")
                    resultados.append({"symbol": symbol, "accion": "ESPERA", "razon": analisis["razon"]})
                    continue
                
                precio_actual = analisis["precio_actual"]
                atr_14 = analisis["atr_14"]
                stop_loss = precio_actual - (2 * atr_14) if atr_14 > 0 else precio_actual * 0.95
                
                evaluacion_riesgo = self.risk_manager.evaluar_operacion(
                    symbol=symbol, capital_actual=capital_actual,
                    capital_inicial=self.capital_inicial, confianza_ia=confianza_ia_default
                )
                
                if not evaluacion_riesgo["autorizado"]:
                    logger.warning(f"🛑 {symbol}: Bloqueado por Risk Manager. Razón: {evaluacion_riesgo['razon']}")
                    resultados.append({"symbol": symbol, "accion": "BLOQUEADO", "razon": evaluacion_riesgo["razon"]})
                    continue
                
                position_sizer = PositionSizer(capital_actual)
                tamaño_posicion = position_sizer.calcular_tamaño_posicion(
                    precio_entrada=precio_actual, stop_loss=stop_loss,
                    factor_ia=evaluacion_riesgo["factor_riesgo"]
                )
                
                if tamaño_posicion["acciones"] <= 0:
                    logger.warning(f"⚠️ {symbol}: Posición inválida. Razón: {tamaño_posicion['razon']}")
                    resultados.append({"symbol": symbol, "accion": "RECHAZADO", "razon": tamaño_posicion["razon"]})
                    continue
                
                riesgo_por_accion = precio_actual - stop_loss
                take_profit = precio_actual + (2 * riesgo_por_accion)
                
                order_data = {
                    "symbol": symbol, "qty": tamaño_posicion["acciones"], "side": OrderSide.BUY,
                    "type": "market", "time_in_force": TimeInForce.DAY, "order_class": OrderClass.BRACKET,
                    "take_profit": {"limit_price": round(take_profit, 2)},
                    "stop_loss": {"stop_price": round(stop_loss, 2)}
                }
                
                orden = self.trading_client.submit_order(order_data=order_data)
                logger.info(f"🎯 {symbol}: Orden Bracket ejecutada. ID: {orden.id}")
                
                resultados.append({
                    "symbol": symbol, "accion": "COMPRADO", "orden_id": orden.id,
                    "cantidad": tamaño_posicion["acciones"], "precio_entrada": round(precio_actual, 2),
                    "stop_loss": round(stop_loss, 2), "take_profit": round(take_profit, 2),
                    "riesgo_pct": tamaño_posicion["riesgo_pct"]
                })
            except Exception as e:
                logger.error(f"❌ Error procesando {symbol}: {e}")
                resultados.append({"symbol": symbol, "accion": "ERROR", "razon": str(e)[:100]})
                
        return {"status": "completado", "resultados": resultados}
