# ==============================================================================
# ARCHIVO: strategy_engine.py
# MODULO: trading
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Motor de estrategias de trading. Evalúa datos de mercado y genera
#            señales de COMPRA, VENTA o ESPERA con justificación lógica.
# ULTIMA MODIFICACION: 2026-07-29
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# ==============================================================================
# [MOD-2026-07-29] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Corrección de ventana móvil de RSI para evaluar los últimos 14 periodos.
# REF: Estrategia de Reversión a la Media (RSI) con confirmación de Volumen.

import logging

logger = logging.getLogger(__name__)

def evaluar_estrategia_rsi_volumen(bars: list, ticker: str) -> dict:
    """
    Estrategia: Reversión a la Media con RSI < 30 (Sobreventa) y Volumen > Promedio.
    Calcula el RSI sobre una ventana móvil de los últimos 14 periodos.
    """
    if not bars or len(bars) < 15:
        return {"senal": "ESPERA", "razon": "Datos insuficientes para calcular RSI (min 15 velas)."}
    
    # Asegurar que los valores sean flotantes
    cierres = [float(bar['c']) for bar in bars]
    volumenes = [float(bar['v']) for bar in bars]
    
    period = 14
    # Tomar los últimos 15 precios para obtener 14 cambios de precio
    recent_cierres = cierres[-period-1:]
    recent_volumenes = volumenes[-period:]
    
    ganancias = []
    perdidas = []
    
    for i in range(1, len(recent_cierres)):
        cambio = recent_cierres[i] - recent_cierres[i-1]
        if cambio > 0:
            ganancias.append(cambio)
            perdidas.append(0.0)
        else:
            ganancias.append(0.0)
            perdidas.append(abs(cambio))
            
    avg_gain = sum(ganancias) / period
    avg_loss = sum(perdidas) / period
    
    if avg_loss == 0:
        rsi = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        
    # Evaluar Volumen (¿El último volumen es mayor al promedio de los últimos 14?)
    avg_volume = sum(recent_volumenes) / period
    ultimo_volumen = volumenes[-1]
    volumen_confirmado = ultimo_volumen > (avg_volume * 1.2) # 20% por encima del promedio
    
    # Lógica de Decisión
    if rsi < 30.0 and volumen_confirmado:
        return {
            "senal": "COMPRA",
            "razon": f"RSI en sobreventa ({rsi:.1f} < 30) con volumen alto ({ultimo_volumen:.0f} > {avg_volume:.0f}).",
            "rsi": rsi,
            "volumen_ok": True
        }
    elif rsi > 70.0:
        return {
            "senal": "ESPERA",
            "razon": f"RSI en sobrecompra ({rsi:.1f} > 70).",
            "rsi": rsi,
            "volumen_ok": False
        }
    else:
        return {
            "senal": "ESPERA",
            "razon": f"RSI neutro ({rsi:.1f}).",
            "rsi": rsi,
            "volumen_ok": volumen_confirmado
        }
