# ==============================================================================
# ARCHIVO: strategy_engine.py
# MODULO: trading
# DEPARTAMENTO: 03 - NEXUS (Trading)
# SISTEMA: MAESTRO-NEXUS
# ROL: El Estratega Cuantitativo
# MISIÓN: Evaluar estrategias de trading (RSI + Volumen) sobre datos históricos.
# DEBERES: Calcular RSI con ventana móvil de 14 periodos, confirmar volumen sobre promedio, devolver señales.
# PROHIBICIONES: Ejecutar órdenes, modificar datos de mercado.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

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
# MOTIVO: Ajuste de parámetros a RSI < 35 y Vol >= 90% para capturar reversiones
#         realistas en activos de fuerte tendencia como AAPL, manteniendo conservadurismo.
# REF: Estrategia de Reversión a la Media (RSI) con confirmación de Volumen.

import logging

logger = logging.getLogger(__name__)

def evaluar_estrategia_rsi_volumen(bars: list, ticker: str) -> dict:
    """
    Estrategia: Reversión a la Media con RSI < 35 y Volumen >= 90% del promedio.
    Calcula el RSI sobre una ventana móvil de los últimos 14 periodos.
    """
    if not bars or len(bars) < 15:
        return {"senal": "ESPERA", "razon": "Datos insuficientes para calcular RSI (min 15 velas)."}
    
    cierres = [float(bar['c']) for bar in bars]
    volumenes = [float(bar['v']) for bar in bars]
    
    period = 14
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
        
    avg_volume = sum(recent_volumenes) / period
    ultimo_volumen = volumenes[-1]
    
    # Ajuste: Volumen >= 90% del promedio (captura agotamiento de venta o volumen normal)
    volumen_confirmado = ultimo_volumen >= (avg_volume * 0.9)
    
    # Lógica de Decisión Ajustada
    if rsi < 35.0 and volumen_confirmado:
        return {
            "senal": "COMPRA",
            "razon": f"RSI en sobreventa ({rsi:.1f} < 35) con volumen válido ({ultimo_volumen:.0f} >= {avg_volume*0.9:.0f}).",
            "rsi": rsi,
            "volumen_ok": True
        }
    elif rsi > 65.0:
        return {
            "senal": "ESPERA",
            "razon": f"RSI en zona alta ({rsi:.1f} > 65).",
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
