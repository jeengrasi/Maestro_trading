# ==============================================================================
# ARCHIVO: risk_manager.py
# MODULO: trading
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Firewall matemático y de reglas para validar operaciones antes de ejecución.
# ULTIMA MODIFICACION: 2026-07-28
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# ==============================================================================
# [MOD-2026-07-28] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Separar la validación de riesgo de la ejecución para blindar el capital (Fase 9.2).
# REF: Principio de Separación de Responsabilidades y Protección Patrimonial (Art. 14).

import logging
from SOBERANO_03_NEXUS.config import Config

logger = logging.getLogger(__name__)

async def validate_trade(ticker: str, side: str, qty: float, redis_client) -> dict:
    """
    Valida una operación contra las reglas de riesgo inquebrantables del sistema.
    Retorna: {"allowed": True, "reason": "OK"} o {"allowed": False, "reason": "Motivo del rechazo"}
    """
    # 1. Verificar Freno de Emergencia (Circuit Breaker) - Regla Absoluta
    cb_active = redis_client.get("circuit_breaker:active")
    cb_val = cb_active.decode() if isinstance(cb_active, bytes) else (cb_active or "")
    if cb_val == "true":
        logger.warning(f"⛔ TRADE RECHAZADO: {ticker} {side} {qty} | Motivo: Circuit Breaker activo")
        return {"allowed": False, "reason": "🔴 Freno de Emergencia (Circuit Breaker) activo. Operaciones suspendidas."}

    # 2. Validaciones básicas de sanidad (Sanity Checks)
    if not isinstance(qty, (int, float)) or qty <= 0:
        return {"allowed": False, "reason": "⚠️ Cantidad inválida. Debe ser un número mayor a 0."}
    
    if side not in ["buy", "sell"]:
        return {"allowed": False, "reason": "⚠️ Lado de la operación no válido. Debe ser 'buy' o 'sell'."}

    # 3. (Espacio reservado para futuras validaciones: VIX > 20, Max Drawdown, etc.)
    # El módulo está diseñado para escalar con nuevas reglas sin tocar el motor de ejecución.

    logger.info(f"✅ TRADE APROBADO POR RISK MANAGER: {ticker} {side} {qty}")
    return {"allowed": True, "reason": "OK"}
