# ==============================================================================
# ARCHIVO: router.py
# MODULO: core
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Orquestador central. Recibe el texto del usuario, detecta la intención
#            (comandos o lenguaje natural) y delega al módulo correspondiente.
# ULTIMA MODIFICACION: 2026-07-28
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# ==============================================================================
# [MOD-2026-07-28] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Extraer lógica de enrutamiento de index.py para mantenerlo como conector delgado.
# REF: Principio de Separación de Responsabilidades (Fase 7/8).

import re
import logging
from SOBERANO_03_NEXUS.config import Config

logger = logging.getLogger(__name__)

async def procesar_intencion(text: str, chat_id: int, redis_client, send_telegram_func):
    """
    Analiza el texto de entrada y lo enruta a la función o módulo correcto.
    Soporta tanto comandos con '/' como lenguaje natural.
    """
    text_lower = text.lower().strip()

    # 1. GESTIÓN: Estado del Sistema
    if text_lower in ["estado", "cómo está el sistema", "como esta el sistema", "resumen", "status", "/estado"]:
        cb = redis_client.get("circuit_breaker:active")
        cb_val = cb.decode() if isinstance(cb, bytes) else (cb or "")
        cb_status = "🔴 ACTIVO" if cb_val == "true" else "🟢 INACTIVO"
        auto_exec = "🟢 ACTIVADO" if Config.AUTO_EJECUCION else "🔴 DESACTIVADO"
        wl_raw = redis_client.get("trading:watchlist")
        wl_val = wl_raw.decode() if isinstance(wl_raw, bytes) else (wl_raw or "")
        wl = wl_val if wl_val else "AAPL,TSLA,NVDA,SPY,QQQ"
        
        msg = f"📊 *ESTADO DEL SISTEMA NEXUS*\n\n"
        msg += f"🛡️ Freno de Emergencia: {cb_status}\n"
        msg += f"⚙️ Ejecución Autónoma: {auto_exec}\n"
        msg += f"👁️ Watchlist Actual: `{wl}`"
        await send_telegram_func(msg, chat_id=chat_id)
        return True

    # 2. GESTIÓN: Ver Watchlist
    elif any(frase in text_lower for frase in ["qué vigila", "que vigila", "lista de activos", "muéstrame la lista", "/watchlist"]):
        wl_raw = redis_client.get("trading:watchlist")
        wl = (wl_raw.decode().split(",") if isinstance(wl_raw, bytes) else wl_raw.split(",")) if wl_raw else ["AAPL", "TSLA", "NVDA", "SPY", "QQQ"]
        lista = "\n".join([f"• {t}" for t in wl])
        await send_telegram_func(f"👁️ *ACTIVOS EN VIGILANCIA:*\n\n{lista}", chat_id=chat_id)
        return True

    # 3. GESTIÓN: Agregar a Watchlist
    elif any(frase in text_lower for frase in ["agrega", "añade", "quiero vigilar", "monitorea", "incluye"]):
        match = re.search(r'\b[A-Z]{2,5}\b', text.upper())
        if match:
            ticker = match.group(0)
            wl_raw = redis_client.get("trading:watchlist")
            wl = (wl_raw.decode().split(",") if isinstance(wl_raw, bytes) else wl_raw.split(",")) if wl_raw else ["AAPL", "TSLA", "NVDA", "SPY", "QQQ"]
            if ticker in wl:
                await send_telegram_func(f"⚠️ *{ticker}* ya está en la lista.", chat_id=chat_id)
            else:
                wl.append(ticker)
                redis_client.set("trading:watchlist", ",".join(wl))
                await send_telegram_func(f"✅ *{ticker}* agregado exitosamente a la vigilancia.", chat_id=chat_id)
            return True

    # 4. GESTIÓN: Eliminar de Watchlist
    elif any(frase in text_lower for frase in ["quita", "elimina", "saca", "deja de vigilar"]):
        match = re.search(r'\b[A-Z]{2,5}\b', text.upper())
        if match:
            ticker = match.group(0)
            wl_raw = redis_client.get("trading:watchlist")
            wl = (wl_raw.decode().split(",") if isinstance(wl_raw, bytes) else wl_raw.split(",")) if wl_raw else ["AAPL", "TSLA", "NVDA", "SPY", "QQQ"]
            if ticker in wl:
                wl.remove(ticker)
                redis_client.set("trading:watchlist", ",".join(wl))
                await send_telegram_func(f"🗑️ *{ticker}* eliminado de la vigilancia.", chat_id=chat_id)
            else:
                await send_telegram_func(f"⚠️ *{ticker}* no se encuentra en la lista.", chat_id=chat_id)
            return True

    # 5. TRADING: Análisis de Sombra (Comando o mención directa de ticker)
    elif text.startswith("/sombra ") or (len(text) <= 5 and text.isalpha() and text.isupper()):
        ticker = text.replace("/sombra ", "").strip().upper()
        from SOBERANO_03_NEXUS.trading.engine import analizar_y_ejecutar_sombra
        await analizar_y_ejecutar_sombra(ticker, redis_client, send_telegram_func, chat_id)
        return True

    # 6. AUTONOMÍA: Trigger manual del scheduler
    elif text_lower in ["/trigger-scheduler", "ejecuta el escaneo", "escanea el mercado ahora"]:
        from SOBERANO_03_NEXUS.autonomy.scheduler import ejecutar_analisis_periodico
        await ejecutar_analisis_periodico(redis_client, send_telegram_func, chat_id)
        return True

    # 7. PARLAMENTO: Debate general con IA (Fallback)
    else:
        from SOBERANO_03_NEXUS.parliament.core import call_ia
        # Clasificación básica de intención para elegir el rol
        rol = "gerente"
        if any(p in text_lower for p in ["riesgo", "peligro", "seguro"]): rol = "auditor"
        elif any(p in text_lower for p in ["precio", "tendencia", "gráfico", "datos"]): rol = "analista"
        elif any(p in text_lower for p in ["comprar", "vender", "inversión", "oportunidad"]): rol = "estratega"
        
        respuesta = await call_ia(rol, text, redis_client=redis_client)
        await send_telegram_func(respuesta, chat_id=chat_id)
        return True
