# ==============================================================================
# ARCHIVO: backtester.py
# MODULO: autonomy
# DEPARTAMENTO: 03 - NEXUS (Autonomía)
# SISTEMA: MAESTRO-NEXUS
# ROL: El Historiador de Mercado
# MISIÓN: Simular operaciones históricas para validar estrategias antes de operar en vivo.
# DEBERES: Usar 100% API nativa de Alpaca, calcular Win Rate/Drawdown/Retorno, devolver veredicto APTO/REQUIERE AJUSTE.
# PROHIBICIONES: Ejecutar órdenes en tiempo real, modificar estrategias.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

# ==============================================================================
# ARCHIVO: backtester.py
# MODULO: autonomy
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Simular operaciones históricas para validar la rentabilidad y 
#            el control de riesgo de la estrategia antes de operar en vivo.
# ULTIMA MODIFICACION: 2026-07-29
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# ==============================================================================
# [MOD-2026-07-29] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Fase 15 - Validación histórica obligatoria antes de cualquier despliegue operativo.
# REF: Constitución v7.1 (Art. 14: Riesgo controlado), Norma EDVC v1.0.

import os
import httpx
import logging
from SOBERANO_03_NEXUS.trading.strategy_engine import evaluar_estrategia_rsi_volumen
from SOBERANO_03_NEXUS.trading.position_sizer import calcular_tamano_posicion

logger = logging.getLogger(__name__)

async def ejecutar_backtest(ticker: str, dias: int = 180) -> dict:
    """
    Ejecuta una simulación histórica de la estrategia en el ticker dado.
    """
    try:
        # 1. Obtener datos históricos de Alpaca
        api_key = os.getenv("ALPACA_API_KEY")
        api_secret = os.getenv("ALPACA_SECRET_KEY")
        headers = {"APCA-API-KEY-ID": api_key, "APCA-API-SECRET-KEY": api_secret}
        
        # Usamos timeframe 1Day para consistencia con la estrategia
        url = f"https://data.alpaca.markets/v2/stocks/{ticker}/bars?timeframe=1Day&limit={dias}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url, headers=headers)
            
        if r.status_code != 200 or not r.json().get("bars"):
            return {"error": f"No se pudieron obtener datos históricos para {ticker}."}
            
        bars = r.json()["bars"]
        
        # 2. Variables de simulación
        capital_inicial = 10000.0
        capital_actual = capital_inicial
        trades_totales = 0
        trades_ganadores = 0
        max_drawdown = 0.0
        pico_capital = capital_inicial
        
        # 3. Bucle de simulación (empezamos en el día 15 para tener datos de RSI)
        for i in range(15, len(bars)):
            datos_historicos = bars[:i+1]
            precio_actual = float(datos_historicos[-1]["c"])
            
            # Evaluar estrategia
            resultado_estrategia = evaluar_estrategia_rsi_volumen(datos_historicos, ticker)
            
            if resultado_estrategia["senal"] == "COMPRA":
                # Calcular posición con factor 0.4
                stop_loss = precio_actual * 0.95 # 5% SL
                sizing = calcular_tamano_posicion(capital_actual, precio_actual, stop_loss, 0.01)
                
                if sizing.get("senal") == "APROBADO":
                    acciones = sizing["acciones"]
                    costo = acciones * precio_actual
                    
                    # Simular salida: Tomamos ganancia al 10% o Stop Loss al 5%
                    # Para simplificar la simulación, buscamos el próximo pico o valle en los siguientes 20 días
                    precio_entrada = precio_actual
                    precio_salida = precio_entrada
                    max_precio = precio_entrada
                    min_precio = precio_entrada
                    
                    for j in range(1, min(20, len(bars) - i)):
                        p = float(bars[i+j]["c"])
                        if p > max_precio: max_precio = p
                        if p < min_precio: min_precio = p
                        
                        # Condición de salida: +10% o -5%
                        if p >= precio_entrada * 1.10 or p <= precio_entrada * 0.95:
                            precio_salida = p
                            break
                    else:
                        # Si no se activa en 20 días, salimos al precio del día 20
                        precio_salida = float(bars[i+19]["c"]) if (i+19) < len(bars) else precio_entrada

                    # Calcular P&L
                    pnl = (precio_salida - precio_entrada) * acciones
                    capital_actual += pnl
                    trades_totales += 1
                    
                    if pnl > 0:
                        trades_ganadores += 1
                        
                    # Actualizar Max Drawdown
                    if capital_actual > pico_capital:
                        pico_capital = capital_actual
                    drawdown_actual = (pico_capital - capital_actual) / pico_capital
                    if drawdown_actual > max_drawdown:
                        max_drawdown = drawdown_actual

        # 4. Calcular métricas finales
        win_rate = (trades_ganadores / trades_totales * 100) if trades_totales > 0 else 0.0
        retorno_total = ((capital_actual - capital_inicial) / capital_inicial) * 100
        
        return {
            "ticker": ticker,
            "dias_simulados": dias,
            "capital_inicial": capital_inicial,
            "capital_final": round(capital_actual, 2),
            "retorno_total_pct": round(retorno_total, 2),
            "trades_totales": trades_totales,
            "win_rate_pct": round(win_rate, 2),
            "max_drawdown_pct": round(max_drawdown * 100, 2),
            "veredicto": "APTO" if (win_rate >= 40 and max_drawdown <= 15 and retorno_total > 0) else "REQUIERE AJUSTE"
        }
        
    except Exception as e:
        logger.error(f"Error en backtest: {e}")
        return {"error": str(e)[:100]}
