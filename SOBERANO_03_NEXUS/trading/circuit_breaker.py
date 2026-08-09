import os
import logging

logger = logging.getLogger(__name__)

def check_daily_drawdown(current_equity: float, starting_equity: float) -> bool:
    """
    Evalúa el drawdown intradía. Retorna True si se debe detener el trading (HALT).
    """
    if starting_equity <= 0:
        return False
        
    drawdown_pct = (starting_equity - current_equity) / starting_equity
    
    if drawdown_pct >= 0.02:  # Umbral institucional del 2.0%
        logger.critical(f"🚨 CIRCUIT BREAKER: Drawdown de {drawdown_pct:.2%} detectado. Bloqueando operaciones.")
        # Lógica de ejecución real (se inyectarán los clientes en el siguiente paso):
        # redis_client.set("SYSTEM_HALT", "TRUE", ex=86400)
        # alpaca_client.cancel_all_orders()
        # send_telegram_alert("🚨 KILL-SWITCH: Drawdown 2% activado. Sistema pausado.")
        return True
        
    return False
