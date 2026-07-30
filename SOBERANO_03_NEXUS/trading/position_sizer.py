# ==============================================================================
# ARCHIVO: position_sizer.py
# MODULO: trading
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Calcular el tamaño exacto de la posición para garantizar que el 
#            riesgo nunca exceda el 1% del capital (Art. 14), con factor de seguridad 0.4.
# ULTIMA MODIFICACION: 2026-07-29
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# ==============================================================================
# [MOD-2026-07-29] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Fase 14 - Blindaje matemático del capital antes de cualquier ejecución.
# REF: Constitución v7.1 (Art. 14), Memoria de Usuario (Factor de seguridad 0.4).

import logging

logger = logging.getLogger(__name__)

def calcular_tamano_posicion(capital_total: float, precio_entrada: float, precio_stop_loss: float, riesgo_maximo_pct: float = 0.01) -> dict:
    """
    Calcula cuántas acciones comprar para que, si se activa el Stop Loss, 
    la pérdida sea exactamente el % de riesgo definido (por defecto 1%).
    Se aplica un factor de seguridad del 0.4x sobre el riesgo calculado para mayor conservadurismo.
    """
    if precio_entrada <= 0 or precio_stop_loss <= 0:
        return {"error": "Precios inválidos para el cálculo de riesgo."}
        
    # 1. Calcular riesgo por acción
    riesgo_por_accion = abs(precio_entrada - precio_stop_loss)
    if riesgo_por_accion == 0:
        return {"error": "El precio de entrada y el stop loss no pueden ser iguales."}
        
    # 2. Calcular monto total a arriesgar (con factor de seguridad 0.4)
    # Ej: Si el capital es $10,000 y riesgo es 1% ($100), el factor 0.4 lo reduce a $40 de riesgo real.
    factor_seguridad = 0.4
    monto_riesgo_ajustado = (capital_total * riesgo_maximo_pct) * factor_seguridad
    
    # 3. Calcular número de acciones
    acciones_a_comprar = int(monto_riesgo_ajustado / riesgo_por_accion)
    
    # 4. Calcular costo total de la operación
    costo_total = acciones_a_comprar * precio_entrada
    
    if acciones_a_comprar < 1:
        return {
            "senal": "RECHAZADO",
            "razon": f"El capital es insuficiente para operar con el riesgo ajustado. Se necesitan al menos 1 acción.",
            "acciones": 0,
            "costo_total": 0
        }
        
    return {
        "senal": "APROBADO",
        "acciones": acciones_a_comprar,
        "costo_total": round(costo_total, 2),
        "riesgo_real_usd": round(riesgo_por_accion * acciones_a_comprar, 2),
        "mensaje": f"Posición calculada: {acciones_a_comprar} acciones. Riesgo real: ${round(riesgo_por_accion * acciones_a_comprar, 2)} (Factor 0.4 aplicado)."
    }
