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
# MOTIVO: Fase 14 - Dotar al sistema de una estrategia Alpha probada y de bajo riesgo.
# REF: Estrategia de Reversión a la Media (RSI) con confirmación de Volumen.

import logging

logger = logging.getLogger(__name__)

def evaluar_estrategia_rsi_volumen(bars: list, ticker: str) -> dict:
    """
    Estrategia: Reversión a la Media con RSI < 30 (Sobreventa) y Volumen > Promedio.
    Es conservadora, ideal para modo Paper y validación inicial.
    """
    if not bars or len(bars) < 14:
        return {"senal": "ESPERA", "razon": "Datos insuficientes para calcular RSI (min 14 velas)."}
    
    # 1. Calcular RSI simple (últimos 14 periodos)
    cierres = [bar['c'] for bar in bars]
    volumenes = [bar['v'] for bar in bars]
    
    # Cálculo simplificado de RSI para evitar dependencias pesadas como pandas/ta-lib en Vercel
    ganancias = []
    perdidas = []
    for i in range(1, 14):
        cambio = cierres[i] - cierres[i-1]
        if cambio > 0:
            ganancias.append(cambio)
            perdidas.append(0)
        else:
            ganancias.append(0)
            perdidas.append(abs(cambio))
            
    avg_gain = sum(ganancias) / 14
    avg_loss = sum(perdidas) / 14
    
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
    # 2. Evaluar Volumen (¿El último volumen es mayor al promedio de los últimos 14?)
    avg_volume = sum(volumenes) / 14
    ultimo_volumen = volumenes[-1]
    volumen_confirmado = ultimo_volumen > (avg_volume * 1.2) # 20% por encima del promedio
    
    # 3. Lógica de Decisión
    if rsi < 30 and volumen_confirmado:
        return {
            "senal": "COMPRA",
            "razon": f"RSI en sobreventa ({rsi:.1f} < 30) con confirmación de volumen alto ({ultimo_volumen} > {avg_volume:.0f}).",
            "rsi": rsi,
            "volumen_ok": True
        }
    elif rsi > 70:
        return {
            "senal": "ESPERA",
            "razon": f"RSI en sobrecompra ({rsi:.1f} > 70). Riesgo de corrección.",
            "rsi": rsi,
            "volumen_ok": False
        }
    else:
        return {
            "senal": "ESPERA",
            "razon": f"RSI neutro ({rsi:.1f}). No se cumplen condiciones de sobreventa + volumen.",
            "rsi": rsi,
            "volumen_ok": volumen_confirmado
        }
