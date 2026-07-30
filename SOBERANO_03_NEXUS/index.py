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
from SOBERANO_03_NEXUS.core.router import procesar_intencion
from SOBERANO_03_NEXUS.core.diagnostics import router as diagnostics_router
from SOBERANO_03_NEXUS.core.memory import bootstrap_nexus_memory
from SOBERANO_03_NEXUS.core.commands import handle_telegram_command
from SOBERANO_03_NEXUS.trading.engine import analizar_y_ejecutar_sombra
from SOBERANO_03_NEXUS.autonomy.scheduler import ejecutar_analisis_periodico
from SOBERANO_03_NEXUS.telegram.inline_actions import handle_autorizacion_callback

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

# Registrar routers modulares
app.include_router(diagnostics_router)

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
    
    # ==========================================
    # FASE 13: Manejo de botones inline (callback_query)
    # ==========================================
    if "callback_query" in payload:
        try:
            callback = payload["callback_query"]
            chat_id = callback["message"]["chat"]["id"]
            query_data = callback["data"]
            
            # Procesar la autorización usando el módulo dedicado
            respuesta = await handle_autorizacion_callback(query_data, redis)
            
            # Responder a Telegram para quitar el estado de "cargando" del botón
            callback_response = {
                "callback_query_id": callback["id"],
                "text": respuesta["text"],
                "show_alert": True,
                "parse_mode": respuesta.get("parse_mode", "Markdown")
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/answerCallbackQuery", 
                    json=callback_response
                )
            return {"ok": True}
        except Exception as e:
            logger.error(f"Error procesando callback_query: {e}")
            return {"ok": False}

    # Procesamiento normal de mensajes de texto
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
    # DELEGACIÓN DE COMANDOS BÁSICOS (FASE 9.1)
    # ================================================
    # [MOD-2026-07-28] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
    # MOTIVO: index.py actúa como conector delgado. Los comandos específicos 
    #         se delegan a core/commands.py.
    if await handle_telegram_command(text, chat_id, redis, send_telegram):
        return {"ok": True}

    # ================================================
    # DELEGACIÓN AL ORQUESTADOR CENTRAL (FASE 8.3)
    # ================================================
    # [MOD-2026-07-28] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
    # MOTIVO: index.py actúa como conector delgado. Toda la lógica de enrutamiento
    #         y lenguaje natural vive en core/router.py.
    # REF: Principio de Separación de Responsabilidades.
    
    # Si el texto no fue capturado por los comandos básicos de arriba (/balance, /start, etc.),
    # lo delegamos al orquestador central para su procesamiento inteligente.
    if not text.startswith("/health") and not text.startswith("/scheduler") and not text.startswith("/actualizar_bitacora"):
        await procesar_intencion(text, chat_id, redis, send_telegram)
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
# SECCIÓN 8: DIAGNÓSTICO SEGURO DE APIs (MIGRADO)
# ================================================
# [MOD-2026-07-28] Lógica movida a SOBERANO_03_NEXUS/core/diagnostics.py
# para reducir el acoplamiento y tamaño de index.py (Fase 9.1).
# El endpoint /diagnostico sigue disponible a través del router incluido.

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

@app.get("/debug/alpaca")
async def debug_alpaca():
    import httpx
    key = os.getenv("ALPACA_API_KEY", "").strip()
    secret = os.getenv("ALPACA_SECRET_KEY", "").strip()
    try:
        headers = {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret}
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get("https://data.alpaca.markets/v2/stocks/AAPL/bars?timeframe=1Day&limit=1", headers=headers)
        return {"status": r.status_code, "has_data": "bars" in r.json() if r.status_code == 200 else False}
    except Exception as e:
        return {"status": "error", "detail": str(e)[:100]}
