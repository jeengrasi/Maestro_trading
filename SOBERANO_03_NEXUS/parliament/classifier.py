# ==============================================================================
# ARCHIVO: classifier.py
# DEPARTAMENTO: 03 - NEXUS (Parlamento)
# SISTEMA: MAESTRO-NEXUS
# ROL: Clasificador de Intenciones
# MISIÓN: Determinar el rol del Parlamento (Gerente, Auditor, etc.) según el input.
# DEBERES: Cumplir con la Constitución, no hardcodear credenciales, registrar errores.
# PROHIBICIONES: Violar las reglas transversales del Manifiesto de Roles.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

def classify_intent(text: str) -> dict:
    text_lower = text.lower()
    trading_keywords = ["comprar", "vender", "btc", "eth", "alpaca", "trading", "invertir", "acción", "acciones"]
    
    if any(k in text_lower for k in trading_keywords):
        return {"role": "estratega", "department": "trading", "confidence": 0.9}
    
    return {"role": "gerente", "department": "debate", "confidence": 0.8}
