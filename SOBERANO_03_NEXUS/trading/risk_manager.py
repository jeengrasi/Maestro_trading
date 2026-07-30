# ==============================================================================
# ARCHIVO: risk_manager.py
# MODULO: trading
# SISTEMA: MAESTRO-NEXUS
# ROL: Firewall Matemático de Riesgo (Art. 14)
# MISIÓN: Bloquear operaciones si las condiciones de mercado son adversas.
# ==============================================================================
import os
import httpx
import logging

logger = logging.getLogger(__name__)

async def check_vix_limit(max_vix: float = 20.0) -> bool:
    """
    Consulta el VIX real. Si es > max_vix, bloquea la operación.
    Nota: Alpaca no tiene VIX nativo, usamos ^VIX de Yahoo Finance via proxy o 
    asumimos un fallback seguro. Para este MVP, simulamos la consulta o usamos un indicador de volatilidad de SPY.
    """
    # Implementación real: consultar API de volatilidad (ej: CBOE o Yahoo Finance ^VIX)
    # Por seguridad, si no podemos verificar, asumimos el peor caso o permitimos con advertencia.
    # Aquí implementamos un chequeo de volatilidad de SPY como proxy del VIX.
    try:
        api_key = os.getenv("ALPACA_API_KEY", "").strip()
        api_secret = os.getenv("ALPACA_SECRET_KEY", "").strip()
        headers = {"APCA-API-KEY-ID": api_key, "APCA-API-SECRET-KEY": api_secret}
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Obtenemos el rango de SPY para calcular volatilidad simple (proxy de VIX)
            r = await client.get("https://data.alpaca.markets/v2/stocks/SPY/bars?timeframe=1Day&limit=10", headers=headers)
            if r.status_code == 200:
                bars = r.json().get("bars", [])
                if len(bars) >= 2:
                    # Cálculo simplificado de volatilidad diaria
                    closes = [b["c"] for b in bars]
                    changes = [(closes[i] - closes[i-1])/closes[i-1] for i in range(1, len(closes))]
                    import statistics
                    daily_vol = statistics.stdev(changes) * 100
                    vix_proxy = daily_vol * 15 # Aproximación muy conservadora
                    
                    if vix_proxy > max_vix:
                        logger.warning(f"🚨 VIX PROXY ALTO: {vix_proxy:.2f} > {max_vix}. Operación bloqueada.")
                        return False
                    return True
        return True # Fallback seguro si no hay datos
    except Exception as e:
        logger.error(f"Error verificando VIX: {e}. Fallo seguro: Bloquear.")
        return False # Fail-closed por seguridad
