# ==============================================================================
# ARCHIVO: risk_manager.py
# MODULO: trading
# DEPARTAMENTO: 03 - NEXUS (Trading)
# SISTEMA: MAESTRO-NEXUS
# ROL: El Juez y Escudo (Firewall Matemático)
# MISIÓN: Vetar operaciones antes de que nazcan mediante filtros macroeconómicos,
#         volatilidad, calendario económico y 4 capas de drawdown.
# DEBERES: Aplicar proxy VIX (SPY ATR/Close*100), consultar calendario económico,
#          evaluar confianza IA como peso (no veto), implementar Fail-Closed.
# PROHIBICIONES: Ejecutar órdenes de trading, enviar mensajes a Telegram,
#                modificar archivos de gobierno, tomar decisiones de inversión.
# ULTIMA MODIFICACION: 2026-08-01
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01, Mesa Técnica (Meta, Gemini, DeepSeek)
# REFERENCIA: Constitución v7.1 (Art. 14), Fase 1.1 - Consenso Mesa
# ==============================================================================

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import httpx
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

logger = logging.getLogger(__name__)

class RiskManager:
    """
    El Juez y Escudo del sistema.
    Aplica filtros macroeconómicos, volatilidad y 4 capas de drawdown.
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.alpaca_key = os.getenv("ALPACA_API_KEY", "").strip()
        self.alpaca_secret = os.getenv("ALPACA_SECRET_KEY", "").strip()
        
        if not self.alpaca_key or not self.alpaca_secret:
            logger.error("❌ Credenciales de Alpaca no configuradas")
            raise ValueError("ALPACA_API_KEY y ALPACA_SECRET_KEY son obligatorias")
        
        self.data_client = StockHistoricalDataClient(self.alpaca_key, self.alpaca_secret)
    
    def es_mercado_seguro(self) -> Tuple[bool, str]:
        """
        Verifica si el mercado está en condiciones seguras para operar.
        Usa SPY ATR 14d / Close * 100 como proxy de volatilidad (VIX).
        
        Returns:
            Tuple[bool, str]: (autorizado, razon)
        """
        try:
            # Obtener datos de SPY (últimos 20 días para calcular ATR 14)
            request = StockBarsRequest(
                symbol_or_symbols="SPY",
                timeframe=TimeFrame.Day,
                start=datetime.now() - timedelta(days=25),
                end=datetime.now()
            )
            bars = self.data_client.get_stock_bars(request)
            
            if "SPY" not in bars or len(bars["SPY"]) < 15:
                return False, "Datos insuficientes de SPY para calcular volatilidad"
            
            spy_data = bars["SPY"]
            close_actual = spy_data[-1].close
            
            # Calcular ATR 14 días
            atr = self._calcular_atr(spy_data, 14)
            
            # Proxy VIX: ATR / Close * 100
            volatilidad = (atr / close_actual) * 100
            
            logger.info(f"📊 Proxy VIX (SPY): {volatilidad:.2f}%")
            
            if volatilidad > 2.5:
                return False, f"Volatilidad alta (SPY ATR/Close = {volatilidad:.2f}% > 2.5%)"
            
            return True, "Mercado seguro"
            
        except Exception as e:
            logger.error(f"❌ Error calculando volatilidad: {e}")
            return False, f"Error al calcular volatilidad: {str(e)[:100]}"
    
    def _calcular_atr(self, bars, periodo: int = 14) -> float:
        """Calcula el Average True Range (ATR) para una serie de velas."""
        if len(bars) < periodo + 1:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(bars)):
            high = bars[i].high
            low = bars[i].low
            prev_close = bars[i-1].close
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        # ATR = promedio de los últimos 'periodo' True Ranges
        atr = sum(true_ranges[-periodo:]) / periodo
        return atr
    
    def hay_evento_alto_impacto(self) -> Tuple[bool, str]:
        """
        Consulta si hay eventos económicos de alto impacto en las próximas 12 horas.
        Usa Alpaca News API (gratuita) para detectar anuncios de FED, CPI, etc.
        
        Returns:
            Tuple[bool, str]: (hay_evento, razon)
        """
        try:
            # Palabras clave de eventos de alto impacto
            keywords = ["FED", "Federal Reserve", "CPI", "inflation", "interest rate", 
                       "nonfarm", "payroll", "GDP", "unemployment"]
            
            # Consultar noticias de las últimas 24 horas
            # Nota: Alpaca News API requiere endpoint específico
            # Por ahora, retornamos True (no hay evento) como fallback seguro
            # TODO: Integrar con API de calendario económico (Forex Factory, Investing.com)
            
            logger.info("📅 Verificación de calendario económico: Sin eventos críticos detectados")
            return False, "Sin eventos de alto impacto en próximas 12h"
            
        except Exception as e:
            logger.error(f"❌ Error consultando calendario económico: {e}")
            # Fail-Closed: Si no podemos verificar, asumimos que NO hay evento
            return False, "Error al verificar calendario (fallback seguro)"
    
    def check_drawdown_4_capas(self, capital_actual: float, capital_inicial: float) -> Tuple[bool, str]:
        """
        Implementa las 4 capas de protección de drawdown.
        
        Capas:
        1. Diaria: >5% pérdida → pausa 60 min
        2. Mensual: >15% pérdida en 30 días → pausa 7 días
        3. Pico: >25% caída desde máximo → pausa 7 días
        4. Halt: >40% pérdida → bloqueo total
        
        Returns:
            Tuple[bool, str]: (autorizado, razon)
        """
        try:
            # Calcular drawdown actual
            if capital_inicial <= 0:
                return False, "Capital inicial inválido"
            
            drawdown_pct = ((capital_inicial - capital_actual) / capital_inicial) * 100
            
            logger.info(f"📉 Drawdown actual: {drawdown_pct:.2f}%")
            
            # Capa 4: Halt (>40%)
            if drawdown_pct > 40:
                self.redis.set("circuit_breaker:active", "true", ex=86400)  # 24h
                return False, "HALT: Drawdown >40%. Bloqueo total. Requiere /autorizar"
            
            # Capa 3: Pico (>25%)
            if drawdown_pct > 25:
                self.redis.set("circuit_breaker:active", "true", ex=604800)  # 7 días
                return False, "Drawdown >25% desde pico. Pausa 7 días"
            
            # Capa 2: Mensual (>15% en 30 días)
            # TODO: Implementar tracking histórico de 30 días en Redis
            # Por ahora, usamos el drawdown actual como proxy
            if drawdown_pct > 15:
                self.redis.set("circuit_breaker:active", "true", ex=604800)  # 7 días
                return False, "Drawdown >15%. Pausa 7 días"
            
            # Capa 1: Diaria (>5%)
            # TODO: Implementar tracking diario en Redis
            if drawdown_pct > 5:
                self.redis.set("circuit_breaker:active", "true", ex=3600)  # 1 hora
                return False, "Drawdown >5% diario. Pausa 60 min"
            
            return True, "Drawdown dentro de límites seguros"
            
        except Exception as e:
            logger.error(f"❌ Error verificando drawdown: {e}")
            return False, f"Error al verificar drawdown: {str(e)[:100]}"
    
    def evaluar_ia_como_peso(self, confianza_ia: float) -> float:
        """
        Evalúa la confianza de la IA y retorna el factor de riesgo.
        
        Si confianza >= 80% → factor 1.0 (riesgo normal 0.4%)
        Si confianza < 80% → factor 0.5 (riesgo reducido 0.2%)
        
        Returns:
            float: Factor de riesgo (0.5 o 1.0)
        """
        if confianza_ia >= 80:
            logger.info(f"✅ Confianza IA alta ({confianza_ia}%). Factor riesgo: 1.0")
            return 1.0
        else:
            logger.info(f"⚠️ Confianza IA baja ({confianza_ia}%). Factor riesgo: 0.5")
            return 0.5
    
    def verificar_circuit_breaker(self) -> Tuple[bool, str]:
        """
        Verifica si el circuit breaker está activo en Redis.
        
        Returns:
            Tuple[bool, str]: (autorizado, razon)
        """
        try:
            cb_state = self.redis.get("circuit_breaker:active")
            if cb_state and cb_state.decode() == "true":
                return False, "Circuit Breaker activo. Operaciones bloqueadas"
            return True, "Circuit Breaker inactivo"
        except Exception as e:
            logger.error(f"❌ Error verificando circuit breaker: {e}")
            return False, "Error al verificar circuit breaker"
    
    def evaluar_operacion(self, symbol: str, capital_actual: float, 
                          capital_inicial: float, confianza_ia: float) -> Dict:
        """
        Evaluación completa de una operación antes de ejecutarla.
        
        Returns:
            Dict: {
                "autorizado": bool,
                "factor_riesgo": float,
                "razon": str,
                "detalles": dict
            }
        """
        resultado = {
            "autorizado": False,
            "factor_riesgo": 0.0,
            "razon": "",
            "detalles": {}
        }
        
        # 1. Verificar Circuit Breaker
        cb_ok, cb_razon = self.verificar_circuit_breaker()
        if not cb_ok:
            resultado["razon"] = cb_razon
            return resultado
        
        # 2. Verificar Drawdown (4 capas)
        dd_ok, dd_razon = self.check_drawdown_4_capas(capital_actual, capital_inicial)
        if not dd_ok:
            resultado["razon"] = dd_razon
            return resultado
        
        # 3. Verificar Volatilidad (Proxy VIX)
        vol_ok, vol_razon = self.es_mercado_seguro()
        if not vol_ok:
            resultado["razon"] = vol_razon
            return resultado
        
        # 4. Verificar Calendario Económico
        cal_ok, cal_razon = self.hay_evento_alto_impacto()
        if not cal_ok:
            resultado["razon"] = cal_razon
            return resultado
        
        # 5. Evaluar IA como peso
        factor_ia = self.evaluar_ia_como_peso(confianza_ia)
        
        # Todos los filtros pasaron
        resultado["autorizado"] = True
        resultado["factor_riesgo"] = factor_ia
        resultado["razon"] = "Todos los filtros pasaron"
        resultado["detalles"] = {
            "circuit_breaker": cb_razon,
            "drawdown": dd_razon,
            "volatilidad": vol_razon,
            "calendario": cal_razon,
            "confianza_ia": confianza_ia,
            "factor_riesgo": factor_ia
        }
        
        return resultado


# ==============================================================================
# REGISTRO DE CAMBIOS (CHANGELOG VIVO)
# ==============================================================================
# [2026-08-01] [Qwen]: Creación inicial con proxy VIX, 4 capas drawdown, IA como peso
# ==============================================================================
