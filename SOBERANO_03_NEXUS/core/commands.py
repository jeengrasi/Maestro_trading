from SOBERANO_03_NEXUS.autonomy.backtester import ejecutar_backtest
from SOBERANO_03_NEXUS.autonomy.reflexion_agent import generar_reflexion_y_propuesta
# ==============================================================================
# ARCHIVO: commands.py
# MODULO: core
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Manejador centralizado de comandos de Telegram.
# ULTIMA MODIFICACION: 2026-07-28
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# ==============================================================================
# [MOD-2026-07-28] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Extraer lógica de comandos de index.py para cumplir el principio de conector delgado.
# REF: Fase 9.1 - Arquitectura Modular.

import os
import logging
from SOBERANO_03_NEXUS.config import Config

logger = logging.getLogger(__name__)

async def handle_telegram_command(text: str, chat_id: int, redis_client, send_telegram_func) -> bool:
    """
    Procesa los comandos de Telegram. Retorna True si el comando fue manejado,
    False si debe ser delegado al router de lenguaje natural.
    """
    text = text.strip()
    
    if text == "/chatid":
        raw_authorized = redis_client.get("telegram:group_id")
        authorized = raw_authorized.decode() if isinstance(raw_authorized, bytes) else (raw_authorized or "6444278889")
        await send_telegram_func(f"Chat ID: `{chat_id}`\nEsperado: `{authorized}`", chat_id=chat_id)
        return True

    if text == "/balance":
        try:
            from SOBERANO_03_NEXUS.trading.engine import get_alpaca_client
            acc = get_alpaca_client().get_account()
            modo = "🧪 PAPER" if Config.ALPACA_PAPER else "💰 REAL"
            await send_telegram_func(
                f"📊 *CUENTA ALPACA ({modo})*\n\n"
                f"💵 *Equity:* ${float(acc.equity):,.2f}\n"
                f"💸 *Buying Power:* ${float(acc.buying_power):,.2f}",
                chat_id=chat_id
            )
        except Exception as e:
            await send_telegram_func(
                f"⚠️ *Error de conexion con Alpaca*\n\n"
                f"Las claves de API en Vercel son invalidas o estan vacias.\n"
                f"*(Detalle: {str(e)[:60]})*",
                chat_id=chat_id
            )
        return True

    if text == "/start":
        raw_max_vix = redis_client.get("risk:max_vix")
        max_vix = raw_max_vix.decode() if isinstance(raw_max_vix, bytes) else (raw_max_vix or Config.MAX_VIX)
        await send_telegram_func(
            f"🤖 *Maestro AI Online*\n\n"
            f"Configuración:\n"
            f"• VIX Máximo: `{max_vix}`\n"
            f"• Riesgo: `{Config.RISK_PER_TRADE * 100}%`\n\n"
            f"📚 *Comandos:*\n"
            f"/balance - Ver saldo\n"
            f"/rendimiento - Ver ultimas operaciones\n"
            f"/sombra [TICKER] - Analisis y ejecucion autonoma\n"
            f"/estado - Estado del sistema\n"
            f"/watchlist - Gestionar activos vigilados",
            chat_id=chat_id
        )
        return True

    if text == "/stop":
        await send_telegram_func("🛑 *EMERGENCIA ACTIVADA*\n\nSistema pausado. Revisar logs.", chat_id=chat_id)
        return True

    if text == "/health":
        try:
            servicios = {
                "Redis": "✅ Activo" if redis_client.ping() else "❌ Inactivo",
            }
            mensaje = "📊 *Estado de Servicios:*\n\n"
            for servicio, estado in servicios.items():
                mensaje += f"• {servicio}: {estado}\n"
            await send_telegram_func(mensaje, chat_id)
            return True
        except Exception as e:
            await send_telegram_func(f"❌ Error: {str(e)}", chat_id)
            return True

    if text == "/actualizar_bitacora":
        try:
            from SOBERANO_02_CORE.core.generar_bitacora import generar_bitacora
            exito, msg = generar_bitacora()
            if exito:
                await send_telegram_func(f"✅ {msg}", chat_id=chat_id)
            else:
                await send_telegram_func(f"❌ Error: {msg}", chat_id=chat_id)
            return True
        except Exception as e:
            await send_telegram_func(f"❌ Error: {str(e)}", chat_id)
            return True

    if text == "/scheduler":
        try:
            from SOBERANO_02_CORE.core.scheduler import get_scheduler
            scheduler = get_scheduler()
            if scheduler:
                status = scheduler.get_status()
                mensaje = "📋 *Estado del Scheduler:*\n\n"
                mensaje += f"Running: {status['running']}\n\n"
                for name, info in status['tasks'].items():
                    mensaje += f"**{name}**\n  Estado: {info['status']}\n"
                await send_telegram_func(mensaje, chat_id)
            else:
                await send_telegram_func("❌ Scheduler no inicializado.", chat_id)
            return True
        except Exception as e:
            await send_telegram_func(f"❌ Error: {str(e)}", chat_id)
            return True


    if text == "/reflexionar":
        try:
            await send_telegram_func("🔄 *Analizando patrones de bloqueo y generando reflexión...*\n\n_Esto puede tomar unos segundos._", chat_id=chat_id)
            resultado = await generar_reflexion_y_propuesta(redis_client)
            if resultado["status"] == "success":
                await send_telegram_func(f"✅ *REFLEXIÓN COMPLETADA*\n\n{resultado['message']}\n\nEl Director debe revisar el Issue en GitHub para ratificar.", chat_id=chat_id)
            elif resultado["status"] == "skipped":
                await send_telegram_func(f"ℹ️ *SIN DATOS*\n\n{resultado['message']}\n\nEl sistema operó dentro de los parámetros normales.", chat_id=chat_id)
            else:
                await send_telegram_func(f"❌ *ERROR*\n\n{resultado['message']}", chat_id=chat_id)
            return True
        except Exception as e:
            await send_telegram_func(f"❌ Error ejecutando reflexión: {str(e)[:100]}", chat_id=chat_id)
            return True


    if text.startswith("/backtest "):
        try:
            ticker = text.split(" ")[1].strip().upper()
            await send_telegram_func(f"🔄 *EJECUTANDO BACKTEST*\n\nSimulando estrategia en *{ticker}* (últimos 180 días). Esto puede tomar unos segundos...\n\n_El sistema aplicará el factor de seguridad 0.4 y riesgo del 1%._", chat_id=chat_id)
            
            resultado = await ejecutar_backtest(ticker, dias=180)
            
            if "error" in resultado:
                await send_telegram_func(f"❌ *ERROR EN BACKTEST*\n\n{resultado['error']}", chat_id=chat_id)
            else:
                veredicto_emoji = "✅" if resultado["veredicto"] == "APTO" else "⚠️"
                mensaje = (
                    f"{veredicto_emoji} *REPORTE DE BACKTEST: {resultado['ticker']}*\n\n"
                    f"📅 *Días simulados:* {resultado['dias_simulados']}\n"
                    f"💰 *Capital:* ${resultado['capital_inicial']} ➡️ ${resultado['capital_final']}\n"
                    f"📈 *Retorno Total:* {resultado['retorno_total_pct']}%\n"
                    f"🎯 *Win Rate:* {resultado['win_rate_pct']}% ({resultado['trades_totales']} trades)\n"
                    f"📉 *Max Drawdown:* {resultado['max_drawdown_pct']}%\n\n"
                    f"🛡️ *Veredicto:* {resultado['veredicto']}\n\n"
                    f"_Nota: Simulación con factor de seguridad 0.4 y SL 5%._"
                )
                await send_telegram_func(mensaje, chat_id=chat_id)
            return True
        except Exception as e:
            await send_telegram_func(f"❌ *ERROR*\n\nUso correcto: `/backtest AAPL`\nDetalle: {str(e)[:50]}", chat_id=chat_id)
            return True

    # Si no es un comando básico, retornar False para que el router lo maneje
    return False
