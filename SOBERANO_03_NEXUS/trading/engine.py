# ==============================================================================
# ARCHIVO: engine.py
# MODULO: trading
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Motor de Trading - Logica de analisis autonomo y ejecucion de ordenes.
# ULTIMA MODIFICACION: 2026-07-28
# AUTOR: Gerente (Qwen) | VALIDADO POR: Mesa Tecnica (Meta, Gemini)
# ==============================================================================
# [MOD-2026-07-28] [AUTOR: Qwen] [VALIDADOR: META, GEMINI, JEISSON_01]
# MOTIVO: Extraer logica de trading de index.py a modulo independiente (Fase 7).
# REF: Dictamen Mesa Tecnica AUDIT-MODULAR-FASE7-META-007

import os
import httpx
import logging
from datetime import datetime
from SOBERANO_03_NEXUS.config import Config
from SOBERANO_03_NEXUS.trading import risk_manager
from SOBERANO_03_NEXUS.config import get_auto_ejecucion_state

logger = logging.getLogger(__name__)

async def analizar_y_ejecutar_sombra(ticker: str, redis_client, send_telegram_func, chat_id: int) -> dict:
    """
    Analiza un activo usando datos nativos de Alpaca, consulta al Parlamento Nexus,
    y ejecuta la orden si AUTO_EJECUCION=true y la decision es COMPRA.
    
    Args:
        ticker: Simbolo del activo (ej: AAPL, TSLA)
        redis_client: Cliente Redis para memoria y freno de emergencia
        send_telegram_func: Funcion para enviar mensajes a Telegram
        chat_id: ID del chat de Telegram
    
    Returns:
        dict con el resultado del analisis y ejecucion
    """
    ticker = ticker.strip().upper()
    await send_telegram_func(f"🔍 *Iniciando analisis autonomo para {ticker}...*", chat_id=chat_id)
    
    try:
        # 1. Freno de Emergencia (Circuit Breaker)
        cb_active = redis_client.get("circuit_breaker:active")
        if cb_active and cb_active.decode() == "true":
            await send_telegram_func("🔴 *FRENOS ACTIVADOS*: El sistema ha detectado rendimiento inferior al 40%. Trading autonomo suspendido hasta revision del Director.", chat_id=chat_id)
            return {"status": "blocked", "reason": "circuit_breaker"}

        # 2. Obtencion de datos de mercado via Alpaca Market Data (Nativo y 100% fiable en Vercel)
        api_key_data = os.getenv("ALPACA_API_KEY")
        api_secret_data = os.getenv("ALPACA_SECRET_KEY")
        headers_data = {"APCA-API-KEY-ID": api_key_data, "APCA-API-SECRET-KEY": api_secret_data}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            url_datos = f"https://data.alpaca.markets/v2/stocks/{ticker}/bars?timeframe=1Day&limit=5"
            r_datos = await client.get(url_datos, headers=headers_data)
            
        if r_datos.status_code != 200 or not r_datos.json().get("bars"):
            await send_telegram_func(f"⚠️ *Error*: No se encontraron datos de mercado para {ticker}. Verifique que el ticker sea correcto (ej: AAPL, TSLA).", chat_id=chat_id)
            return {"status": "error", "reason": "no_data"}
            
        bars = r_datos.json()["bars"]
        precio = float(bars[-1]["c"])  # Precio de cierre mas reciente
        precio_ref = float(bars[-3]["c"]) if len(bars) >= 3 else precio  # Precio de hace 3 dias para tendencia
        volumen = int(bars[-1]["v"])
        tendencia = "ALCISTA 📈" if precio > precio_ref else "BAJISTA 📉"
        
        # 3. Debate del Parlamento (Analista + Auditor con concision)
        from SOBERANO_03_NEXUS.parliament.core import call_ia
        prompt_analista = f"Actua como Analista y Auditor. Activo: {ticker}. Precio: {precio}. Tendencia 5d: {tendencia}. Volumen: {volumen}. Regla de oro: Riesgo max 1%. Da un veredicto de COMPRA o VENTA con 1 razon principal. Max 60 palabras."
        
        decision_ia = await call_ia("estratega", prompt_analista, redis_client=redis_client)
        
        # 4. Logica de Ejecucion
        es_compra = "COMPRA" in decision_ia.upper()
        modo = "🧪 PAPER" if Config.ALPACA_PAPER else "💰 REAL"
        mensaje_ejecucion = f"📊 *ANALISIS AUTONOMO: {ticker}*\n\n💵 Precio: ${precio:.2f}\n📈 Tendencia: {tendencia}\n🧠 Decision IA:\n_{decision_ia}_\n\n"
        
        resultado = {
            "status": "analyzed",
            "ticker": ticker,
            "precio": precio,
            "tendencia": tendencia,
            "volumen": volumen,
            "decision_ia": decision_ia,
            "es_compra": es_compra,
            "ejecutado": False
        }
        
        if es_compra and Config.AUTO_EJECUCION:

        
            # 1. VALIDACIÓN DE RIESGO OBLIGATORIA (Fase 9.2 - Nexus Contralor)

        
            risk_check = await risk_manager.validate_trade(ticker, "buy", 1, redis_client)

        
            if not risk_check["allowed"]:

        
                mensaje_ejecucion += f"⛔ *ORDEN BLOQUEADA POR RIESGO*: {risk_check['reason']}"

        
                resultado["status"] = "blocked_by_risk"

        
            else:

        
                # 2. EJECUCIÓN (Solo si el Risk Manager aprueba)

        
                api_key_ord = os.getenv("ALPACA_API_KEY")

        
                api_secret_ord = os.getenv("ALPACA_SECRET_KEY")

        
                is_paper = os.getenv("ALPACA_PAPER", "true").strip().lower() == "true"

        
                base_url = "https://paper-api.alpaca.markets" if is_paper else "https://api.alpaca.markets"

        
                

        
                headers_ord = {"APCA-API-KEY-ID": api_key_ord, "APCA-API-SECRET-KEY": api_secret_ord}

        
                payload = {"symbol": ticker, "qty": 1, "side": "buy", "type": "market", "time_in_force": "day"}

        
                

        
                async with httpx.AsyncClient(timeout=10.0) as client:

        
                    r_ord = await client.post(f"{base_url}/v2/orders", headers=headers_ord, json=payload)

        
                    

        
                if r_ord.status_code == 200:

        
                    mensaje_ejecucion += f"✅ *EJECUCION AUTONOMA ({modo})*: Orden de COMPRA de 1 accion enviada exitosamente."

        
                    redis_client.lpush("memoria:trades:autonomos", f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] COMPRA {ticker} @ {precio}")

        
                    resultado["ejecutado"] = True

        
                    resultado["status"] = "executed"

        
                else:

        
                    mensaje_ejecucion += f"❌ *FALLO DE EJECUCION*: {r_ord.text[:100]}"

        
                    resultado["status"] = "execution_failed"


        elif es_compra and not Config.AUTO_EJECUCION:
            mensaje_ejecucion += f"⏸️ *SEÑAL DE COMPRA DETECTADA*, pero AUTO_EJECUCION esta desactivado en Config."
        else:
            mensaje_ejecucion += "⏸️ *SEÑAL DE ESPERA/VENTA*. No se ejecuta accion."
            
        await send_telegram_func(mensaje_ejecucion, chat_id=chat_id)
        return resultado
        
    except Exception as e:
        logger.error(f"Error en modo sombra: {e}", exc_info=True)
        await send_telegram_func(f"❌ *Error en modo sombra*: {str(e)[:100]}", chat_id=chat_id)
        return {"status": "error", "reason": str(e)[:100]}
