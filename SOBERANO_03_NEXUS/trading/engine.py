# ==============================================================================
# ARCHIVO: engine.py
# MODULO: trading
# DEPARTAMENTO: 03 - NEXUS (Trading)
# SISTEMA: MAESTRO-NEXUS
# ROL: El Ejecutor Blindado
# MISIÓN: Analizar mercados, calcular riesgo y ejecutar órdenes solo con autorización temporal.
# DEBERES: Verificar Circuit Breaker, consultar AUTO_EJECUCION_TEMP, integrar Position Sizer (factor 0.4) y Risk Manager.
# PROHIBICIONES: Enviar mensajes a Telegram, manejar memoria conversacional, ejecutar sin autorización válida.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

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
from SOBERANO_03_NEXUS.trading.strategy_engine import evaluar_estrategia_rsi_volumen
from SOBERANO_03_NEXUS.trading.position_sizer import calcular_tamano_posicion

logger = logging.getLogger(__name__)

async def analizar_y_ejecutar_sombra(ticker: str, redis_client, send_telegram_func, chat_id: int) -> dict:
    """
    Analiza un activo usando datos nativos de Alpaca, evalúa la estrategia (Fase 14),
    calcula el riesgo (Fase 14), verifica autorización (Fase 13) y ejecuta si corresponde.
    """
    try:
        # 1. Verificar Circuit Breaker
        win_rate = redis_client.get("metricas:win_rate")
        if win_rate and float(win_rate) < 0.40:
            await send_telegram_func("🔴 *FRENOS ACTIVADOS*: Rendimiento inferior al 40%. Trading suspendido.", chat_id=chat_id)
            return {"status": "blocked", "reason": "circuit_breaker"}

        # 2. Obtención de datos de mercado via Alpaca
        api_key_data = os.getenv("ALPACA_API_KEY")
        api_secret_data = os.getenv("ALPACA_SECRET_KEY")
        headers_data = {"APCA-API-KEY-ID": api_key_data, "APCA-API-SECRET-KEY": api_secret_data}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            url_datos = f"https://data.alpaca.markets/v2/stocks/{ticker}/bars?timeframe=1Day&limit=14"
            r_datos = await client.get(url_datos, headers=headers_data)
            
        if r_datos.status_code != 200 or not r_datos.json().get("bars"):
            await send_telegram_func(f"⚠️ *Error*: No se encontraron datos para {ticker}.", chat_id=chat_id)
            return {"status": "error", "reason": "no_data"}
            
        bars = r_datos.json()["bars"]
        precio = float(bars[-1]["c"])
        tendencia = "ALCISTA" if bars[-1]["c"] > bars[0]["c"] else "BAJISTA"
        
        # 3. Evaluación con Cerebro Financiero (Fase 14)
        resultado_estrategia = evaluar_estrategia_rsi_volumen(bars, ticker)
        senal = resultado_estrategia["senal"]
        razon_estrategia = resultado_estrategia["razon"]
        
        es_compra = (senal == "COMPRA")
        modo = "🧪 PAPER" if os.getenv("ALPACA_PAPER", "true").lower() == "true" else "💰 REAL"
        
        mensaje = f"📊 *ANÁLISIS AUTÓNOMO: {ticker}*\n\n"
        mensaje += f"💵 *Precio:* ${precio:.2f}\n"
        mensaje += f"📈 *Tendencia:* {tendencia}\n"
        mensaje += f"🧠 *Señal:* {senal}\n"
        mensaje += f"📝 *Razón:* {razon_estrategia}\n\n"
        
        resultado = {
            "status": "analyzed",
            "ticker": ticker,
            "precio": precio,
            "senal": senal,
            "ejecutado": False
        }
        
        # 4. Lógica si la señal es COMPRA
        if es_compra:
            # 4.1 Cálculo de Posición (Fase 14: Blindaje Matemático con factor 0.4)
            capital_base = float(os.getenv("CAPITAL_BASE", "10000.0"))
            precio_stop_loss = precio * 0.95
            
            sizing = calcular_tamano_posicion(capital_base, precio, precio_stop_loss, riesgo_maximo_pct=0.01)
            
            if sizing.get("senal") == "RECHAZADO":
                mensaje += f"🚫 *RIESGO:* {sizing['razon']}\n\n"
                resultado["status"] = "rejected_by_sizer"
            else:
                mensaje += f"🛡️ *Position Sizing:* {sizing['mensaje']}\n\n"
                
                # 4.2 Verificación de Autorización Temporal (Fase 13)
                if not get_auto_ejecucion_state(redis_client):
                    mensaje += "⚠️ *MODO SOMBRA*: Ejecución automática desactivada o expirada.\n\n"
                    resultado["status"] = "shadow_pending_auth"
                else:
                    # 4.3 Ejecución Real
                    api_key_ord = os.getenv("ALPACA_API_KEY")
                    api_secret_ord = os.getenv("ALPACA_SECRET_KEY")
                    is_paper = os.getenv("ALPACA_PAPER", "true").lower() == "true"
                    base_url = "https://paper-api.alpaca.markets" if is_paper else "https://api.alpaca.markets"
                    
                    qty = sizing.get("acciones", 1)
                    payload = {
                        "symbol": ticker,
                        "qty": qty,
                        "side": "buy",
                        "type": "market",
                        "time_in_force": "day"
                    }
                    headers_ord = {"APCA-API-KEY-ID": api_key_ord, "APCA-API-SECRET-KEY": api_secret_ord}
                    
                    async with httpx.AsyncClient(timeout=10.0) as client_ord:
                        r_ord = await client_ord.post(f"{base_url}/v2/orders", headers=headers_ord, json=payload)
                        
                    if r_ord.status_code == 200:
                        mensaje += f"✅ *ORDEN EJECUTADA* en {modo}.\n\n"
                        resultado["ejecutado"] = True
                        resultado["status"] = "executed"
                    else:
                        mensaje += f"❌ *FALLO DE EJECUCIÓN*: {r_ord.text[:100]}\n\n"
                        resultado["status"] = "execution_failed"

        # 5. Construir botones inline y enviar mensaje (Fase 13)
        inline_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ AUTORIZAR AUTO 1H", "callback_data": f"AUTH_{ticker}"},
                    {"text": "👁️ SOLO SOMBRA", "callback_data": f"SHADOW_{ticker}"}
                ]
            ]
        }
        await send_telegram_func(mensaje, chat_id=chat_id, reply_markup=inline_keyboard)
        
        return resultado
        
    except Exception as e:
        await send_telegram_func(f"❌ *ERROR CRÍTICO* en análisis de {ticker}: {str(e)[:100]}", chat_id=chat_id)
        return {"status": "error", "reason": str(e)[:100]}
