# ==============================================================================
# ARCHIVO: strategy_engine.py
# MODULO: trading
# DEPARTAMENTO: 03 - NEXUS (Trading)
# SISTEMA: MAESTRO-NEXUS
# ROL: El Analista Técnico
# MISIÓN: Calcular confluencia de indicadores (EMA 200 + RSI 14 + Volumen) para
#         generar señales de COMPRA/VENTA/ESPERA en timeframe 1H.
# DEBERES: Usar API nativa de Alpaca (data.alpaca.markets), calcular indicadores
#          técnicos, retornar señales estructuradas.
# PROHIBICIONES: Ejecutar órdenes, modificar datos de mercado, enviar Telegram.
# ULTIMA MODIFICACION: 2026-08-01
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01, Mesa Técnica
# REFERENCIA: Constitución v7.1 (Art. 14), Fase 1.1 - Consenso Mesa
# ==============================================================================

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import numpy as np
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

logger = logging.getLogger(__name__)

class StrategyEngine:
    """
    El Analista Técnico del sistema.
    Calcula confluencia EMA 200 + RSI 14 + Volumen para generar señales.
    """
    
    def __init__(self):
        self.alpaca_key = os.getenv("ALPACA_API_KEY", "").strip()
        self.alpaca_secret = os.getenv("ALPACA_SECRET_KEY", "").strip()
        
        if not self.alpaca_key or not self.alpaca_secret:
            logger.error("❌ Credenciales de Alpaca no configuradas")
            raise ValueError("ALPACA_API_KEY y ALPACA_SECRET_KEY son obligatorias")
        
        self.data_client = StockHistoricalDataClient(self.alpaca_key, self.alpaca_secret)
    
    def calcular_ema(self, precios: list, periodo: int) -> Optional[float]:
        """Calcula la Media Móvil Exponencial (EMA) para un periodo dado."""
        if len(precios) < periodo:
            return None
        
        # EMA = precio_actual * k + EMA_anterior * (1 - k)
        # donde k = 2 / (periodo + 1)
        k = 2 / (periodo + 1)
        
        # Inicializar EMA con SMA de los primeros 'periodo' valores
        ema = sum(precios[:periodo]) / periodo
        
        # Calcular EMA para el resto
        for precio in precios[periodo:]:
            ema = precio * k + ema * (1 - k)
        
        return ema
    
    def calcular_rsi(self, precios: list, periodo: int = 14) -> Optional[float]:
        """Calcula el Índice de Fuerza Relativa (RSI)."""
        if len(precios) < periodo + 1:
            return None
        
        # Calcular cambios
        cambios = [precios[i] - precios[i-1] for i in range(1, len(precios))]
        
        # Separar ganancias y pérdidas
        ganancias = [c if c > 0 else 0 for c in cambios]
        perdidas = [abs(c) if c < 0 else 0 for c in cambios]
        
        # Promedio de ganancias y pérdidas
        avg_ganancia = sum(ganancias[-periodo:]) / periodo
        avg_perdida = sum(perdidas[-periodo:]) / periodo
        
        if avg_perdida == 0:
            return 100.0
        
        rs = avg_ganancia / avg_perdida
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calcular_atr(self, bars, periodo: int = 14) -> Optional[float]:
        """Calcula el Average True Range (ATR) para Stop Loss dinámico."""
        if len(bars) < periodo + 1:
            return None
        
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
        
        atr = sum(true_ranges[-periodo:]) / periodo
        return atr
    
    def calcular_confluencia(self, symbol: str) -> Dict:
        """
        Calcula la confluencia de indicadores para un símbolo dado.
        
        Condiciones para COMPRA:
        1. Precio > EMA 200 (tendencia alcista)
        2. RSI 14 entre 40 y 70 (no sobrecomprado/sobrevendido)
        3. Volumen > 120% del promedio de 20 periodos
        
        Returns:
            Dict: {
                "symbol": str,
                "señal": "COMPRA" | "VENTA" | "ESPERA",
                "precio_actual": float,
                "ema_200": float,
                "rsi_14": float,
                "volumen_actual": int,
                "volumen_promedio": int,
                "atr_14": float,
                "razon": str
            }
        """
        resultado = {
            "symbol": symbol,
            "señal": "ESPERA",
            "precio_actual": 0.0,
            "ema_200": 0.0,
            "rsi_14": 0.0,
            "volumen_actual": 0,
            "volumen_promedio": 0,
            "atr_14": 0.0,
            "razon": ""
        }
        
        try:
            # Obtener velas de 1H (últimas 250 para calcular EMA 200)
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Hour,
                start=datetime.now() - timedelta(days=40),  # ~250 velas de 1H
                end=datetime.now()
            )
            bars = self.data_client.get_stock_bars(request)
            
            if symbol not in bars or len(bars[symbol]) < 201:
                resultado["razon"] = f"Datos insuficientes para {symbol}"
                return resultado
            
            symbol_bars = bars[symbol]
            
            # Extraer datos
            precios_cierre = [bar.close for bar in symbol_bars]
            volumenes = [bar.volume for bar in symbol_bars]
            
            precio_actual = precios_cierre[-1]
            
            # Calcular indicadores
            ema_200 = self.calcular_ema(precios_cierre, 200)
            rsi_14 = self.calcular_rsi(precios_cierre, 14)
            atr_14 = self.calcular_atr(symbol_bars, 14)
            
            volumen_actual = volumenes[-1]
            volumen_promedio = sum(volumenes[-20:]) / 20
            
            # Actualizar resultado
            resultado["precio_actual"] = precio_actual
            resultado["ema_200"] = ema_200 or 0.0
            resultado["rsi_14"] = rsi_14 or 0.0
            resultado["volumen_actual"] = volumen_actual
            resultado["volumen_promedio"] = int(volumen_promedio)
            resultado["atr_14"] = atr_14 or 0.0
            
            # Evaluar confluencia
            condiciones = []
            
            # 1. Tendencia alcista
            if ema_200 and precio_actual > ema_200:
                condiciones.append("Tendencia alcista (Precio > EMA 200)")
            
            # 2. RSI en zona óptima
            if rsi_14 and 40 < rsi_14 < 70:
                condiciones.append(f"RSI óptimo ({rsi_14:.1f})")
            
            # 3. Volumen confirmado
            if volumen_actual > volumen_promedio * 1.2:
                condiciones.append(f"Volumen alto ({volumen_actual} > {int(volumen_promedio * 1.2)})")
            
            # Si las 3 condiciones se cumplen → COMPRA
            if len(condiciones) == 3:
                resultado["señal"] = "COMPRA"
                resultado["razon"] = "Confluencia completa: " + " + ".join(condiciones)
                logger.info(f"✅ {symbol}: {resultado['razon']}")
            else:
                resultado["señal"] = "ESPERA"
                resultado["razon"] = f"Confluencia incompleta ({len(condiciones)}/3): " + ", ".join(condiciones) if condiciones else "Sin condiciones cumplidas"
                logger.info(f"⏸️ {symbol}: {resultado['razon']}")
            
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error calculando confluencia para {symbol}: {e}")
            resultado["razon"] = f"Error: {str(e)[:100]}"
            return resultado


# ==============================================================================
# REGISTRO DE CAMBIOS (CHANGELOG VIVO)
# ==============================================================================
# [2026-08-01] [Qwen]: Creación inicial con EMA 200 + RSI 14 + Volumen
# ==============================================================================
