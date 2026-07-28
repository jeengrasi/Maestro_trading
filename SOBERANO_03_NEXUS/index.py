# ==============================================================================
# ARCHIVO: index.py
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Punto de entrada FastAPI. Gestiona webhooks de Telegram, comandos 
#            y enrutamiento al debate parlamentario.
# ULTIMA MODIFICACION MAYOR: 2026-07-27
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# DOCUMENTO DE AUDITORIA: SOBERANO_01_MEMORIA/AUDITS/AUDIT-INDEX-2026-07-27.md
# ==============================================================================
# DESCRIPCION: Punto de entrada de la API FastAPI.
# Maneja webhooks de Telegram, comandos y debate parlamentario.
# 
# FIX V3.1 (2026-07-07):
# - Reemplazo de BackgroundTasks por Redis Queue
# - BackgroundTasks NO funciona en Vercel (el contenedor se destruye)
# - Ahora los mensajes se guardan en Redis y un Worker externo los procesa
# - GitHub Actions ejecuta el Worker cada 2 minutos
# - Trazabilidad completa con fechas y observaciones
# ================================================

import os
import sys
import httpx
import logging
import asyncio
import json
from datetime import datetime
from fastapi import FastAPI, Request
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from upstash_redis import Redis
from SOBERANO_03_NEXUS.config import Config
from SOBERANO_03_NEXUS.telegram.utils import send_telegram
from SOBERANO_03_NEXUS.trading.engine import analizar_y_ejecutar_sombra
from SOBERANO_03_NEXUS.autonomy.scheduler import ejecutar_analisis_periodico

# [MOD-2026-07-28] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Preparado para integraciones futuras. Nota: El Modo Sombra usa Alpaca Market Data 
# nativo para evitar bloqueos de yfinance en entornos serverless (Vercel).

# ================================================
# SECCIÓN 2: CONFIGURACIÓN INICIAL
# ================================================

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# ================================================
# SECCIÓN 3: CONEXIONES A SERVICIOS
# ================================================

redis = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
)

_alpaca_client = None

def get_alpaca_client():
    global _alpaca_client
    if _alpaca_client is None:
        _alpaca_client = TradingClient(
            Config.ALPACA_API_KEY,
            Config.ALPACA_SECRET_KEY,
            paper=Config.ALPACA_PAPER
        )
    return _alpaca_client

# ================================================
# SECCIÓN 4: MEMORIA DEL SISTEMA
# ================================================

def bootstrap_nexus_memory(redis_client: Redis):
    try:
        tg_id = redis_client.get("telegram:group_id")
        feat_parliament = redis_client.get("feature:parliament")
        
        if not tg_id or not feat_parliament:
            manifest_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "NEXUS_MANIFEST.json"
            )
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                state = manifest.get("state_declarative", {})
                
                if not tg_id:
                    redis_client.set("telegram:group_id", "6444278889")
                if not feat_parliament:
                    redis_client.set("feature:parliament", "0")
                
                redis_client.set(
                    "risk:max_vix",
                    str(state.get("risk_management", {}).get("max_vix", "20.0"))
                )
                redis_client.set(
                    "nexus:state:last_recovery",
                    datetime.now().isoformat()
                )
                logger.info("✅ Redis auto-hidratado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error en bootstrap de memoria: {e}", exc_info=True)

# ================================================
# SECCIÓN 5: ENDPOINTS DE LA API
# ================================================

@app.get("/")
async def root():
    return {"status": "running", "system": "Maestro-Nexus"}

@app.get("/health")
async def health():
    start = datetime.now()
    try:
        r = await asyncio.wait_for(
            asyncio.to_thread(redis.ping),
            timeout=2.0
        )
        redis_ok = (r == "PONG" or r is True)
    except:
        redis_ok = False
    
    return {
        "status": "ok" if redis_ok else "degraded",
        "redis": redis_ok,
        "latency_ms": round((datetime.now() - start).total_seconds() * 1000, 2)
    }

@app.get("/webhook")
async def webhook_verification():
    return {"status": "ok"}

# ================================================
# SECCION 6: WEBHOOK PRINCIPAL DE TELEGRAM
# ================================================
# [CONTEXTO ARQUITECTONICO]
# MOTIVO: Vercel destruye los contenedores serverless inmediatamente despues 
# de responder, matando las tareas en segundo plano (BackgroundTasks).
# SOLUCION: Los mensajes se encolan en Redis y son procesados por un Worker 
# externo (GitHub Actions) o sincronicamente si la confianza es alta.
# ================================================
# 2026-07-07 - V3.1: Usa Redis Queue en lugar de BackgroundTasks

@app.post("/webhook")
async def telegram_webhook(req: Request):
    payload = await req.json()
    message = payload.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")
    
    bootstrap_nexus_memory(redis)
    
    raw_authorized_chat = redis.get("telegram:group_id")
    authorized_chat = raw_authorized_chat or "6444278889"
    
    if chat_id != int(authorized_chat):
        logger.warning(f"⚠️ Chat no autorizado: {chat_id}")
        return {"ok": False}

    # ================================================
    # COMANDO: /chatid
    # ================================================
    if text == "/chatid":
        await send_telegram(
            f"Chat ID: `{chat_id}`\nEsperado: `{authorized_chat}`",
            chat_id=chat_id
        )
        return {"ok": True}

    # ================================================
    # COMANDO: /balance
    # ================================================
    if text == "/balance":
        # [MOD-2026-07-27] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
        # MOTIVO: Proteger webhook de colapso 500 por credenciales de Alpaca invalidas.
        # REF: Log de error 401-Alpaca-Unauthorized (2026-07-27)
        try:
            acc = get_alpaca_client().get_account()
            modo = "🧪 PAPER" if Config.ALPACA_PAPER else "💰 REAL"
            await send_telegram(
                f"📊 *CUENTA ALPACA ({modo})*\n\n"
                f"💵 *Equity:* ${float(acc.equity):,.2f}\n"
                f"💸 *Buying Power:* ${float(acc.buying_power):,.2f}",
                chat_id=chat_id
            )
        except Exception as e:
            await send_telegram(
                f"⚠️ *Error de conexion con Alpaca*\n\n"
                f"Las claves de API en Vercel son invalidas o estan vacias.\n"
                f"*(Detalle: {str(e)[:60]})*",
                chat_id=chat_id
            )
        return {"ok": True}

    # ================================================
    # COMANDO: /rendimiento
    # ================================================
    if text == "/rendimiento":
        # [MOD-2026-07-28] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
        # MOTIVO: Obtener historial de operaciones usando httpx directo para evitar errores de importacion de alpaca-py en Vercel.
        # REF: Fase 4 - Analisis de rendimiento y estrategia. Principio de Resiliencia.
        try:
            api_key = os.getenv("ALPACA_API_KEY")
            api_secret = os.getenv("ALPACA_SECRET_KEY")
            is_paper = os.getenv("ALPACA_PAPER", "true").strip().lower() == "true"
            base_url = "https://paper-api.alpaca.markets" if is_paper else "https://api.alpaca.markets"
            
            headers = {
                "APCA-API-KEY-ID": api_key,
                "APCA-API-SECRET-KEY": api_secret
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Solicitamos las ultimas 10 operaciones de tipo FILL (ejecuciones)
                url = f"{base_url}/v2/account/activities?activity_types=FILL&page_size=10"
                r = await client.get(url, headers=headers)
                r.raise_for_status()
                activities = r.json()
            
            if not activities:
                await send_telegram("📊 *RENDIMIENTO*\n\nNo se encontraron operaciones recientes (FILL) en el historial.", chat_id=chat_id)
                return {"ok": True}
            
            resumen = "📊 *RENDIMIENTO RECIENTE (Ultimas 10 Operaciones)*\n\n"
            for act in activities[:10]:
                simbolo = act.get("symbol", "N/A")
                lado = "COMPRA" if act.get("side") == "buy" else "VENTA"
                cantidad = act.get("qty", 0)
                precio = float(act.get("price", 0))
                # La fecha viene en formato ISO, la simplificamos
                fecha_raw = act.get("transaction_time", act.get("date", "N/A"))
                fecha = fecha_raw[:16].replace("T", " ") if isinstance(fecha_raw, str) else "N/A"
                
                resumen += f"• {fecha} | *{simbolo}* | {lado} {cantidad} @ ${precio:.2f}\n"
            
            resumen += "\n💡 *Nota:* El sistema esta registrando estas operaciones. Para un analisis de Win Rate y P&L acumulado, se activara el modulo de backtracking en la Fase 5."
            
            await send_telegram(resumen, chat_id=chat_id)
            
        except Exception as e:
            await send_telegram(
                f"⚠️ *Error al obtener historial de Alpaca*\n\n"
                f"Verifique que las claves de API sean validas y tengan permisos de lectura.\n"
                f"*(Detalle: {str(e)[:60]})*",
                chat_id=chat_id
            )
        return {"ok": True}

    # ================================================
    # COMANDO: /sombra [TICKER] (MODO SOMBRA AUTONOMO)
    # ================================================
    if text.startswith("/sombra "):
        # [MOD-2026-07-28] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
        # MOTIVO: Modularización Fase 7. Delegación de lógica de trading al motor independiente.
        # REF: Dictamen Mesa Tecnica AUDIT-MODULAR-FASE7-META-007
        ticker = text.replace("/sombra ", "").strip()
        await analizar_y_ejecutar_sombra(ticker, redis, send_telegram, chat_id)
        return {"ok": True}

    # ================================================
    # COMANDOS: GESTIÓN DINÁMICA DEL SISTEMA (FASE 8.1)
    # ================================================
    
    # COMANDO: /estado
    if text == "/estado":
        cb = redis.get("circuit_breaker:active")
        cb_val = cb.decode() if isinstance(cb, bytes) else (cb or "")
        cb_status = "🔴 ACTIVO" if cb_val == "true" else "🟢 INACTIVO"
        
        auto_exec = "🟢 ACTIVADO" if Config.AUTO_EJECUCION else "🔴 DESACTIVADO"
        
        wl_raw = redis.get("trading:watchlist")
        wl_val = wl_raw.decode() if isinstance(wl_raw, bytes) else (wl_raw or "")
        wl = wl_val if wl_val else "AAPL,TSLA,NVDA,SPY,QQQ"
        
        msg = f"📊 *ESTADO DEL SISTEMA NEXUS*\n\n"
        msg += f"🛡️ Freno de Emergencia: {cb_status}\n"
        msg += f"⚙️ Ejecución Autónoma: {auto_exec}\n"
        msg += f"👁️ Watchlist Actual: `{wl}`\n\n"
        msg += f"💡 Use `/watchlist` para gestionar los activos."
        await send_telegram(msg, chat_id=chat_id)
        return {"ok": True}

    # COMANDO: /watchlist
    if text == "/watchlist":
        wl_raw = redis.get("trading:watchlist")
        wl =  (wl_raw.decode().split(",") if isinstance(wl_raw, bytes) else wl_raw.split(",")) if wl_raw else  ["AAPL", "TSLA", "NVDA", "SPY", "QQQ"]
        lista = "\n".join([f"• {t}" for t in wl])
        await send_telegram(f"👁️ *ACTIVOS EN VIGILANCIA:*\n\n{lista}\n\n💡 Use `/watchlist agregar [TICKER]` o `/watchlist eliminar [TICKER]`", chat_id=chat_id)
        return {"ok": True}

    # COMANDO: /watchlist agregar [TICKER]
    if text.startswith("/watchlist agregar "):
        nuevo_ticker = text.replace("/watchlist agregar ", "").strip().upper()
        wl_raw = redis.get("trading:watchlist")
        wl =  (wl_raw.decode().split(",") if isinstance(wl_raw, bytes) else wl_raw.split(",")) if wl_raw else  ["AAPL", "TSLA", "NVDA", "SPY", "QQQ"]
        
        if nuevo_ticker in wl:
            await send_telegram(f"⚠️ *{nuevo_ticker}* ya está en la lista de vigilancia.", chat_id=chat_id)
        else:
            wl.append(nuevo_ticker)
            redis.set("trading:watchlist", ",".join(wl))
            await send_telegram(f"✅ *{nuevo_ticker}* agregado exitosamente a la vigilancia.", chat_id=chat_id)
        return {"ok": True}

    # COMANDO: /watchlist eliminar [TICKER]
    if text.startswith("/watchlist eliminar "):
        ticker_a_eliminar = text.replace("/watchlist eliminar ", "").strip().upper()
        wl_raw = redis.get("trading:watchlist")
        wl =  (wl_raw.decode().split(",") if isinstance(wl_raw, bytes) else wl_raw.split(",")) if wl_raw else  ["AAPL", "TSLA", "NVDA", "SPY", "QQQ"]
        
        if ticker_a_eliminar in wl:
            wl.remove(ticker_a_eliminar)
            redis.set("trading:watchlist", ",".join(wl))
            await send_telegram(f"🗑️ *{ticker_a_eliminar}* eliminado de la vigilancia.", chat_id=chat_id)
        else:
            await send_telegram(f"⚠️ *{ticker_a_eliminar}* no se encuentra en la lista.", chat_id=chat_id)
        return {"ok": True}

    # ================================================
    # COMANDO: /start
    # ================================================
    if text == "/start":
        raw_max_vix = redis.get("risk:max_vix")
        max_vix = raw_max_vix or Config.MAX_VIX
        await send_telegram(
            f"🤖 *Maestro AI Online*\n\n"
            f"Configuración:\n"
            f"• VIX Máximo: `{max_vix}`\n"
            f"• Riesgo: `{Config.RISK_PER_TRADE * 100}%`\n\n"
            f"📚 *Comandos:*\n"
            f"/docs - Listar documentos\n"
            f"/doc <nombre> - Consultar documento\n"
            f"/actas - Listar actas\n"
            f"/balance - Ver saldo\n"
            f"/rendimiento - Ver ultimas operaciones\n"
            f"/sombra [TICKER] - Analisis y ejecucion autonoma (Modo Sombra)\n"
            f"/chatid - Ver ID del chat\n"
            f"/start - Estado del bot\n"
            f"/stop - Pausar el sistema\n"
            f"/scheduler - Estado del scheduler\n"
            f"/health - Estado de servicios\n"
            f"/actualizar_bitacora - Actualizar Bitácora",
            chat_id=chat_id
        )
        return {"ok": True}

    # ================================================
    # COMANDO: /docs
    # ================================================
    if text == "/docs":
        try:
            keys = redis.keys("doc:*")
            if not keys:
                await send_telegram("📄 No hay documentos indexados.", chat_id)
                return {"ok": True}
            
            docs = []
            for key in keys[:10]:
                metadata = redis.hgetall(key)
                ruta = metadata.get(b"ruta", b"").decode()
                if ruta:
                    docs.append(f"- {ruta}")
            
            mensaje = "📄 *Documentos disponibles:*\n\n" + "\n".join(docs)
            await send_telegram(mensaje, chat_id)
            return {"ok": True}
        except Exception as e:
            await send_telegram(f"❌ Error: {str(e)}", chat_id)
            return {"ok": True}

    # ================================================
    # COMANDO: /doc <nombre>
    # ================================================
    if text.startswith("/doc "):
        nombre = text.replace("/doc ", "").strip()
        key = f"doc:{nombre.replace('/', ':')}"
        contenido = redis.hget(key, "contenido")
        
        if contenido:
            contenido_text = contenido.decode()
            if len(contenido_text) > 3000:
                contenido_text = contenido_text[:3000] + "\n\n... (truncado)"
            await send_telegram(f"📄 *{nombre}*\n\n{contenido_text}", chat_id)
            return {"ok": True}
        
        keys = redis.keys(f"doc:*{nombre}*")
        if keys:
            mensaje = f"📄 *Coincidencias para '{nombre}':*\n\n"
            for k in keys[:5]:
                metadata = redis.hgetall(k)
                ruta = metadata.get(b"ruta", b"").decode()
                mensaje += f"- {ruta}\n"
            await send_telegram(mensaje, chat_id)
        else:
            await send_telegram(f"❌ No se encontró: '{nombre}'", chat_id)
        return {"ok": True}

    # ================================================
    # COMANDO: /actas
    # ================================================
    if text == "/actas":
        try:
            keys = redis.keys("doc:01-MEMORIA:DOCS:actas:*")
            if not keys:
                await send_telegram("📋 No hay actas generadas.", chat_id)
                return {"ok": True}
            
            actas = []
            for key in keys:
                metadata = redis.hgetall(key)
                debate_id = metadata.get(b"debate_id", b"").decode()
                fecha = metadata.get(b"fecha_index", b"").decode()
                if debate_id:
                    actas.append(f"- {debate_id} ({fecha[:10]})")
            
            mensaje = "📋 *Actas generadas:*\n\n" + "\n".join(actas)
            await send_telegram(mensaje, chat_id)
            return {"ok": True}
        except Exception as e:
            await send_telegram(f"❌ Error: {str(e)}", chat_id)
            return {"ok": True}

    # ================================================
    # COMANDO: /stop
    # ================================================
    if text == "/stop":
        await send_telegram(
            "🛑 *EMERGENCIA ACTIVADA*\n\nSistema pausado. Revisar logs.",
            chat_id=chat_id
        )
        return {"ok": True}

    # ================================================
    # COMANDO: /actualizar_bitacora
    # ================================================
    if text == "/actualizar_bitacora":
        try:
            from SOBERANO_02_CORE.core.generar_bitacora import generar_bitacora
            exito, msg = generar_bitacora()
            if exito:
                await send_telegram(f"✅ {msg}", chat_id=chat_id)
            else:
                await send_telegram(f"❌ Error: {msg}", chat_id=chat_id)
            return {"ok": True}
        except Exception as e:
            await send_telegram(f"❌ Error: {str(e)}", chat_id)
            return {"ok": True}

    # ================================================
    # COMANDO: /scheduler
    # ================================================
    if text == "/scheduler":
        try:
            from SOBERANO_02_CORE.core.scheduler import get_scheduler
            scheduler = get_scheduler()
            if scheduler:
                status = scheduler.get_status()
                mensaje = "📋 *Estado del Scheduler:*\n\n"
                mensaje += f"Running: {status['running']}\n\n"
                for name, info in status['tasks'].items():
                    mensaje += f"**{name}**\n"
                    mensaje += f"  Intervalo: {info['interval']}s\n"
                    mensaje += f"  Estado: {info['status']}\n"
                    if info['last_run']:
                        mensaje += f"  Última ejecución: {info['last_run'][:16]}\n"
                    mensaje += "\n"
                await send_telegram(mensaje, chat_id)
            else:
                await send_telegram("❌ Scheduler no inicializado.", chat_id)
            return {"ok": True}
        except Exception as e:
            await send_telegram(f"❌ Error: {str(e)}", chat_id)
            return {"ok": True}

    # ================================================
    # COMANDO: /health
    # ================================================
    if text == "/health":
        try:
            from SOBERANO_02_CORE.core.scheduler import get_scheduler
            # [MOD-2026-07-27] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
            # MOTIVO: Evitar que /health colapse si Alpaca tiene credenciales invalidas.
            # REF: Log de error 401-Alpaca-Unauthorized (2026-07-27)
            alpaca_status = "❌ Inactivo"
            try:
                get_alpaca_client().get_account()
                alpaca_status = "✅ Activo"
            except:
                pass
                
            servicios = {
                "Redis": "✅ Activo" if redis.ping() else "❌ Inactivo",
                "Alpaca": alpaca_status,
                "Scheduler": "✅ Activo" if get_scheduler() else "❌ Inactivo"
            }
            mensaje = "📊 *Estado de Servicios:*\n\n"
            for servicio, estado in servicios.items():
                mensaje += f"• {servicio}: {estado}\n"
            await send_telegram(mensaje, chat_id)
            return {"ok": True}
        except Exception as e:
            await send_telegram(f"❌ Error: {str(e)}", chat_id)
            return {"ok": True}

    # ================================================
    # MENSAJES NATURALES - DEBATE PARLAMENTARIO
    # ================================================
    # 2026-07-07 - V3.1: Redis Queue en lugar de BackgroundTasks
    
    if text and not text.startswith("/"):
        try:
            from SOBERANO_03_NEXUS.router import (
                handle_parliament_debate,
                get_manager_recommendation,
                classify_intent,
                call_ia
            )
            from SOBERANO_03_NEXUS.parliament.actas import generate_acta, save_acta_to_github
            
            intent = classify_intent(text)
            
            # [MOD-2026-07-27] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
            # MOTIVO: Umbral >= 1 inalcanzable. >= 0.95 fuerza procesamiento sincrono 
            #         inmediato con el nuevo cerebro Mistral, sin depender del Worker.
            # REF: Analisis forense de classifier.py (2026-07-27)
            if intent["confidence"] >= 0.95:
                # 2026-07-07 - V3.1: Guardar en Redis en lugar de BackgroundTasks
                queue_key = f"queue:debate:{chat_id}:{datetime.now().timestamp()}"
                redis.set(
                    queue_key,
                    json.dumps({"chat_id": chat_id, "text": text}),
                    ex=3600
                )
                
                await send_telegram(
                    "🏛️ *Parlamento Nexus convocado.*\n\n"
                    "⏳ Tu consulta está en cola. Recibirás respuesta en unos minutos.",
                    chat_id=chat_id
                )
                
                return {"ok": True, "status": "queued"}
                
            else:
                role = intent["role"]
                dept_name = intent["department"].capitalize()
                await send_telegram(f"🔍 *Consultando a {dept_name}...*", chat_id=chat_id)
                
                # [MOD-2026-07-27] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
                # MOTIVO: Pasar el cliente Redis a call_ia para persistencia de la memoria en la nube.
                # REF: Migración de bitácora de archivo local a Upstash Redis.
                response_text = await call_ia(role, text, redis_client=redis)
                
                # [MOD-2026-07-27] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
                # MOTIVO: Eliminar truncamiento local. send_telegram ahora maneja 
                #         el Message Chunking automático para respuestas EDVC largas.
                # REF: Fase 3 - Implementación de Message Chunking en utils.py
                await send_telegram(response_text, chat_id)
                return {"ok": True}
                
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            await send_telegram(f"❌ Error: {str(e)}", chat_id)
            return {"ok": True}

    return {"ok": True}

# ================================================
# SECCIÓN 7: FUNCIÓN DEPRECADA (V3.0)
# ================================================
# 2026-07-07 - DEPRECADA: Ya no se usa en V3.1
# Se mantiene por compatibilidad

async def procesar_debate_background(text: str, chat_id: int):
    """
    2026-07-07 - DEPRECADA: Reemplazada por Redis Queue + Worker
    """
    logger.warning("⚠️ procesar_debate_background está DEPRECADO. Usar Redis Queue.")
    try:
        from SOBERANO_03_NEXUS.router import (
            handle_parliament_debate,
            get_manager_recommendation
        )
        from SOBERANO_03_NEXUS.parliament.actas import generate_acta, save_acta_to_github
        from datetime import datetime
        
        logger.info(f"📨 [DEPRECADO] Iniciando debate para chat {chat_id}")
        
        debate_results = await handle_parliament_debate(text)
        recommendation = await get_manager_recommendation(text, debate_results)
        
        acta_content = await generate_acta(text, debate_results, recommendation)
        acta_result = await save_acta_to_github(
            acta_content,
            f"NEXUS-DEB-{datetime.now().strftime('%Y%m%d-%H%M')}"
        )
        
        response_text = "🏛️ *DEBATE PARLAMENTARIO FINALIZADO*\n\n"
        for role, data in debate_results.items():
            resp = data['response']
            if len(resp) > 300:
                resp = resp[:300] + "..."
            response_text += f"*{data['role']} ({data['model']}):*\n{resp}\n\n"
        response_text += f"---\n📋 *RECOMENDACIÓN FINAL:*\n{recommendation}"
        response_text += f"\n\n📄 {acta_result}"
        
        await send_telegram(response_text, chat_id)
        
        logger.info(f"✅ [DEPRECADO] Debate completado para chat {chat_id}")
        
    except Exception as e:
        logger.error(f"❌ Error en debate background (deprecado): {e}", exc_info=True)
        await send_telegram(
            f"❌ Error procesando el debate: {str(e)}\n\n"
            "Por favor, intenta de nuevo más tarde.",
            chat_id=chat_id
        )

# ================================================
# FIN DEL ARCHIVO
# ================================================
# 2026-07-07 - V3.1 COMPLETO
# CAMBIOS REALIZADOS:
# 1. REM: BackgroundTasks de importación
# 2. REM: BackgroundTasks de firma de telegram_webhook
# 3. MOD: Reemplazo de bloque de debate con Redis Queue
# 4. ADD: Comentarios de deprecación
# 5. ADD: Observaciones y fechas en todas las secciones modificadas
# ================================================

# ================================================
# SECCIÓN 7.5: ENDPOINT DE TRIGGER PARA SCHEDULER AUTÓNOMO
# ================================================
# [MOD-2026-07-28] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Permitir que un servicio externo (GitHub Actions/Cron) dispare el análisis periódico.
# REF: Fase 7.2 - Scheduler Autónomo.

@app.get("/trigger-scheduler")
async def trigger_scheduler():
    try:
        # Verificación básica de seguridad (opcional: agregar SCHEDULER_TOKEN en env vars)
        # if os.getenv("SCHEDULER_TOKEN") != "tu_token_secreto":
        #     return {"status": "unauthorized"}, 401
        
        chat_id = int(Config.TELEGRAM_CHAT_ID)
        resultado = await ejecutar_analisis_periodico(redis, send_telegram, chat_id)
        return {"status": "success", "detalle": resultado}
    except Exception as e:
        logger.error(f"Error en trigger-scheduler: {e}", exc_info=True)
        return {"status": "error", "detalle": str(e)[:100]}

# ================================================
# SECCIÓN 8: DIAGNÓSTICO SEGURO DE APIs (SOLO LECTURA)
# ================================================
@app.get("/diagnostico")
async def diagnosticar_apis():
    """
    Prueba la conectividad de todas las APIs configuradas en Vercel.
    TODAS las claves se enmascaran automáticamente para seguridad.
    """
    resultados = {"timestamp": datetime.now().isoformat(), "apis": {}}
    
    def mask_key(key):
        if not key or len(key) < 8: return "NO_CONFIGURADA"
        return f"{key[:4]}****{key[-4:]}"
    
    async def test_llm(name, url, api_key, model, payload_override=None):
        if not api_key:
            resultados["apis"][name] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}
            return
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = payload_override or {"model": model, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 1}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.post(url, headers=headers, json=payload)
                if r.status_code == 200:
                    resultados["apis"][name] = {"estado": "✅ OK", "clave": mask_key(api_key), "http": 200}
                else:
                    resultados["apis"][name] = {"estado": f"❌ FALLÓ ({r.status_code})", "clave": mask_key(api_key), "detalle": r.text[:60]}
        except Exception as e:
            resultados["apis"][name] = {"estado": "❌ ERROR DE RED", "clave": mask_key(api_key), "detalle": str(e)[:50]}

    # 1. IAs de Lenguaje (LLMs)
    await test_llm("Mistral", "https://api.mistral.ai/v1/chat/completions", os.getenv("MISTRAL_API_KEY"), "mistral-tiny")
    await test_llm("DeepSeek", "https://api.deepseek.com/v1/chat/completions", os.getenv("DEEPSEEK_API_KEY"), "deepseek-chat")
    await test_llm("Groq", "https://api.groq.com/openai/v1/chat/completions", os.getenv("GROQ_API_KEY"), "llama3-8b-8192")
    await test_llm("OpenRouter", "https://openrouter.ai/api/v1/chat/completions", os.getenv("OPENROUTER_API_KEY"), "openrouter/auto", {"model": "openrouter/auto", "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 1})
    await test_llm("Cerebras", "https://api.cerebras.ai/v1/chat/completions", os.getenv("CEREBRAS_API_KEY"), "llama3.1-8b")
    
    # NVIDIA NIM
    nim_key = os.getenv("NVIDIA_NIM_API_KEY") or os.getenv("NVIDIA_API_KEY")
    await test_llm("NVIDIA NIM", "https://integrate.api.nvidia.com/v1/chat/completions", nim_key, "meta/llama3-8b-instruct")

    # Google Gemini (Formato especial)
    gemini_key = os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                r = await client.post(url, json={"contents": [{"parts": [{"text": "Hi"}]}]})
                resultados["apis"]["Google Gemini"] = {"estado": "✅ OK" if r.status_code == 200 else f"❌ FALLÓ ({r.status_code})", "clave": mask_key(gemini_key)}
        except Exception as e:
            resultados["apis"]["Google Gemini"] = {"estado": "❌ ERROR", "clave": mask_key(gemini_key), "detalle": str(e)[:50]}
    else:
        resultados["apis"]["Google Gemini"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    # Cloudflare Workers AI
    cf_token = os.getenv("CLOUDFLARE_API_TOKEN")
    cf_account = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    if cf_token and cf_account:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                url = f"https://api.cloudflare.com/client/v4/accounts/{cf_account}/ai/run/@cf/meta/llama-3-8b-instruct"
                r = await client.post(url, headers={"Authorization": f"Bearer {cf_token}"}, json={"messages": [{"role": "user", "content": "Hi"}]})
                resultados["apis"]["Cloudflare AI"] = {"estado": "✅ OK" if r.status_code == 200 else f"❌ FALLÓ ({r.status_code})", "clave": mask_key(cf_token)}
        except Exception as e:
            resultados["apis"]["Cloudflare AI"] = {"estado": "❌ ERROR", "clave": mask_key(cf_token), "detalle": str(e)[:50]}
    else:
        resultados["apis"]["Cloudflare AI"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    # HuggingFace
    hf_key = os.getenv("HUGGINGFACE_API_KEY")
    if hf_key:
        resultados["apis"]["HuggingFace"] = {"estado": "⚠️ CLAVE PRESENTE", "clave": mask_key(hf_key), "nota": "Requiere modelo específico para prueba real"}
    else:
        resultados["apis"]["HuggingFace"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    # 2. Servicios de Infraestructura y Trading
    # Telegram
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if tg_token:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"https://api.telegram.org/bot{tg_token}/getMe")
                resultados["apis"]["Telegram"] = {"estado": "✅ OK" if r.json().get("ok") else "❌ FALLÓ", "clave": mask_key(tg_token)}
        except:
            resultados["apis"]["Telegram"] = {"estado": "❌ ERROR", "clave": mask_key(tg_token)}
    else:
        resultados["apis"]["Telegram"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    # Alpaca
    alpaca_key = os.getenv("ALPACA_API_KEY")
    alpaca_secret = os.getenv("ALPACA_SECRET_KEY")
    if alpaca_key and alpaca_secret:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                headers = {"APCA-API-KEY-ID": alpaca_key, "APCA-API-SECRET-KEY": alpaca_secret}
                is_paper = os.getenv("ALPACA_PAPER", "true").strip().lower() == "true"
                url = "https://paper-api.alpaca.markets/v2/account" if is_paper else "https://api.alpaca.markets/v2/account"
                r = await client.get(url, headers=headers)
                resultados["apis"]["Alpaca"] = {"estado": "✅ OK" if r.status_code == 200 else f"❌ FALLÓ ({r.status_code})", "clave": mask_key(alpaca_key), "modo": "Paper" if is_paper else "Real"}
        except Exception as e:
            resultados["apis"]["Alpaca"] = {"estado": "❌ ERROR", "clave": mask_key(alpaca_key), "detalle": str(e)[:50]}
    else:
        resultados["apis"]["Alpaca"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    # Upstash Redis
    redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
    redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    if redis_url and redis_token:
        try:
            # Usamos el cliente redis ya inicializado en el archivo
            r = await asyncio.wait_for(asyncio.to_thread(redis.ping), timeout=2.0)
            resultados["apis"]["Upstash Redis"] = {"estado": "✅ OK" if (r == "PONG" or r is True) else "❌ FALLÓ", "clave": mask_key(redis_token)}
        except:
            resultados["apis"]["Upstash Redis"] = {"estado": "❌ ERROR", "clave": mask_key(redis_token)}
    else:
        resultados["apis"]["Upstash Redis"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    # GitHub
    gh_token = os.getenv("GITHUB_TOKEN")
    if gh_token:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get("https://api.github.com/user", headers={"Authorization": f"Bearer {gh_token}", "User-Agent": "Nexus-Diagnostic"})
                resultados["apis"]["GitHub"] = {"estado": "✅ OK" if r.status_code == 200 else f"❌ FALLÓ ({r.status_code})", "clave": mask_key(gh_token)}
        except:
            resultados["apis"]["GitHub"] = {"estado": "❌ ERROR", "clave": mask_key(gh_token)}
    else:
        resultados["apis"]["GitHub"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    # Railway (Solo verificación de presencia, no tiene API pública de ping sin project ID)
    railway_token = os.getenv("RAILWAY_TOKEN") or os.getenv("RAILWAY_API_TOKEN")
    if railway_token:
        resultados["apis"]["Railway"] = {"estado": "⚠️ CLAVE PRESENTE", "clave": mask_key(railway_token)}
    else:
        resultados["apis"]["Railway"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    return resultados

# ==============================================================================
# REGISTRO DE CAMBIOS (CHANGELOG VIVO)
# ==============================================================================
# [2026-07-27] Qwen: Migración de memoria de bitácora a Upstash Redis para 
#                     garantizar persistencia de aciertos y errores en Vercel.
# [2026-07-27] Qwen: Aplicacion de Norma EDVC v1.0. Protegidos endpoints /balance 
#                     y /health contra fallos de Alpaca. Ajustado umbral de clasificador.
# [2026-07-07] DeepSeek/Copilot: Migracion inicial a V3.1 (Redis Queue).
# ==============================================================================

# ================================================
# SECCIÓN 9: ENDPOINT DE DEBUG DE ENTORNO (SOLO LECTURA)
# ================================================
# [MOD-2026-07-27] [AUTOR: Qwen] [VALIDADOR: META, GEMINI]
# MOTIVO: Permitir verificación en tiempo real de qué valores lee Vercel.
# REF: AUDIT-401-ALPACA-VERCEL-META-005
@app.get("/debug/env")
async def debug_env():
    return {
        "ALPACA_API_KEY_prefix": os.getenv("ALPACA_API_KEY", "VACIA")[:2] if os.getenv("ALPACA_API_KEY") else "VACIA",
        "ALPACA_PAPER_raw": repr(os.getenv("ALPACA_PAPER", "NO_ENCONTRADA")),
        "ALPACA_PAPER_evaluado": Config.ALPACA_PAPER,
        "TELEGRAM_TOKEN_len": len(os.getenv("TELEGRAM_BOT_TOKEN", ""))
    }
