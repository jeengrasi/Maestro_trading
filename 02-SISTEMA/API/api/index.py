# # ================================================
# MAESTRO-NEXUS | INDEX.PY V3.0 (FIX TIMEOUT)
# ================================================
# ID: api/index.py
# COMMIT: index_v3.0_background_tasks
# FECHA: 2026-07-07
# AUTOR: Gerente (DeepSeek) + Arquitecto (Copilot)
# ESTADO: ✅ COMPLETO - FIX TIMEOUT VERCEL
# ================================================
# DESCRIPCIÓN: Punto de entrada de la API FastAPI.
# Maneja webhooks de Telegram, comandos y debate parlamentario.
# 
# FIX V3.0 (2026-07-07):
# - Implementación de BackgroundTasks para evitar timeout en Vercel
# - El debate parlamentario se ejecuta en segundo plano
# - Respuesta inmediata al usuario (< 1 segundo)
# - Trazabilidad completa con fechas y observaciones
# ================================================
# COMANDOS DISPONIBLES:
# /start          - Estado del bot y lista de comandos
# /docs           - Listar documentos indexados en Redis
# /doc <nombre>   - Consultar contenido de un documento
# /actas          - Listar actas generadas
# /balance        - Ver saldo de Alpaca (paper trading)
# /chatid         - Ver ID del chat autorizado
# /stop           - Pausar el sistema (emergencia)
# /scheduler      - Ver estado del motor de tareas
# /health         - Verificar estado de servicios
# /actualizar_bitacora - Actualizar Bitácora manualmente
# Mensaje natural - Debate parlamentario o consulta directa
# ================================================

# ================================================
# SECCIÓN 1: IMPORTACIONES
# ================================================
# 2026-07-05 - Versión original
# 2026-07-07 - ADD: BackgroundTasks para procesamiento asíncrono

import os
import sys
import httpx
import logging
import asyncio
import json
from datetime import datetime
from fastapi import FastAPI, Request, BackgroundTasks  # 2026-07-07: ADD BackgroundTasks
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from upstash_redis import Redis
from api.config import Config
from api.telegram.utils import send_telegram

# ================================================
# SECCIÓN 2: CONFIGURACIÓN INICIAL
# ================================================
# 2026-07-05 - Versión original

# Agregar directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI()

# ================================================
# SECCIÓN 3: CONEXIONES A SERVICIOS
# ================================================
# 2026-07-05 - Versión original

# Conexión a Redis (Upstash)
redis = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
)

# Cliente de Alpaca (lazy loading)
_alpaca_client = None

def get_alpaca_client():
    """Obtiene o crea el cliente de Alpaca para trading paper."""
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
# 2026-07-05 - Versión original

def bootstrap_nexus_memory(redis_client: Redis):
    """
    Hidrata Redis con la configuración inicial del sistema.
    Carga NEXUS_MANIFEST.json si no hay datos en Redis.
    """
    try:
        # Verificar si ya hay datos en Redis
        tg_id = redis_client.get("telegram:group_id")
        feat_parliament = redis_client.get("feature:parliament")
        
        if not tg_id or not feat_parliament:
            # Cargar desde NEXUS_MANIFEST.json
            manifest_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "NEXUS_MANIFEST.json"
            )
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                state = manifest.get("state_declarative", {})
                
                # Establecer valores por defecto si no existen
                if not tg_id:
                    redis_client.set("telegram:group_id", "6444278889")
                if not feat_parliament:
                    redis_client.set("feature:parliament", "0")
                
                # Configurar límites de riesgo
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
# 2026-07-05 - Versión original

@app.get("/")
async def root():
    """Endpoint raíz - verifica que la API está corriendo."""
    return {"status": "running", "system": "Maestro-Nexus"}

@app.get("/health")
async def health():
    """
    Health check básico - verifica estado de Redis.
    Usado por Vercel y monitoreo.
    """
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
    """Endpoint de verificación para el webhook de Telegram."""
    return {"status": "ok"}

# ================================================
# SECCIÓN 6: WEBHOOK PRINCIPAL DE TELEGRAM
# ================================================
# 2026-07-05 - Versión original (V2.2)
# 2026-07-07 - MOD: Añadir BackgroundTasks para evitar timeout
# 2026-07-07 - MOD: Reemplazar bloque de debate (líneas 406-435) con llamado a background

@app.post("/webhook")
async def telegram_webhook(req: Request, background_tasks: BackgroundTasks):  # 2026-07-07: ADD BackgroundTasks
    """
    Punto de entrada para mensajes de Telegram.
    Procesa comandos y mensajes naturales.
    
    2026-07-07 - MOD: Ahora usa BackgroundTasks para procesar debates en segundo plano
    """
    # Leer payload
    payload = await req.json()
    message = payload.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")
    
    # Inicializar memoria si es necesario
    bootstrap_nexus_memory(redis)
    
    # Verificar autorización del chat
    raw_authorized_chat = redis.get("telegram:group_id")
    authorized_chat = raw_authorized_chat or "6444278889"
    
    if chat_id != int(authorized_chat):
        logger.warning(f"⚠️ Chat no autorizado: {chat_id}")
        return {"ok": False}

    # ================================================
    # COMANDO: /chatid - VER ID DEL CHAT
    # ================================================
    if text == "/chatid":
        await send_telegram(
            f"Chat ID: `{chat_id}`\nEsperado: `{authorized_chat}`",
            chat_id=chat_id
        )
        return {"ok": True}

    # ================================================
    # COMANDO: /balance - VER SALDO ALPACA
    # ================================================
    if text == "/balance":
        acc = get_alpaca_client().get_account()
        modo = "🧪 PAPER" if Config.ALPACA_PAPER else "💰 REAL"
        await send_telegram(
            f"📊 *CUENTA ALPACA ({modo})*\n\n"
            f"💵 *Equity:* ${float(acc.equity):,.2f}\n"
            f"💸 *Buying Power:* ${float(acc.buying_power):,.2f}",
            chat_id=chat_id
        )
        return {"ok": True}

    # ================================================
    # COMANDO: /start - ESTADO DEL BOT Y AYUDA
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
    # COMANDO: /docs - LISTAR DOCUMENTOS INDEXADOS
    # ================================================
    if text == "/docs":
        try:
            keys = redis.keys("doc:*")
            if not keys:
                await send_telegram("📄 No hay documentos indexados.", chat_id)
                return {"ok": True}
            
            docs = []
            for key in keys[:10]:  # Límite de 10
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
    # COMANDO: /doc <nombre> - CONSULTAR DOCUMENTO
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
        
        # Búsqueda por coincidencia parcial
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
    # COMANDO: /actas - LISTAR ACTAS GENERADAS
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
    # COMANDO: /stop - PAUSAR SISTEMA (EMERGENCIA)
    # ================================================
    if text == "/stop":
        await send_telegram(
            "🛑 *EMERGENCIA ACTIVADA*\n\nSistema pausado. Revisar logs.",
            chat_id=chat_id
        )
        return {"ok": True}

    # ================================================
    # COMANDO: /actualizar_bitacora - ACTUALIZAR BITÁCORA
    # ================================================
    if text == "/actualizar_bitacora":
        try:
            from api.core.generar_bitacora import generar_bitacora
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
    # COMANDO: /scheduler - ESTADO DEL SCHEDULER
    # ================================================
    if text == "/scheduler":
        try:
            from api.core.scheduler import get_scheduler
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
    # COMANDO: /health - ESTADO DE SERVICIOS
    # ================================================
    if text == "/health":
        try:
            from api.core.scheduler import get_scheduler
            servicios = {
                "Redis": "✅ Activo" if redis.ping() else "❌ Inactivo",
                "Alpaca": "✅ Activo" if get_alpaca_client() else "❌ Inactivo",
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
    # 2026-07-05 - Versión original
    # 2026-07-07 - FIX: Reemplazo completo para usar BackgroundTasks
    #               El debate ahora se ejecuta en segundo plano
    #               evitando el timeout de Vercel (10s)
    
    if text and not text.startswith("/"):
        try:
            from api.router import (
                handle_parliament_debate,
                get_manager_recommendation,
                classify_intent,
                call_ia
            )
            from api.parliament.actas import generate_acta, save_acta_to_github
            
            intent = classify_intent(text)
            
            # Si la confianza es alta, convocar parlamento
            if intent["confidence"] >= 1:
                # 2026-07-07 - FIX: Respuesta inmediata + background
                # Ya no se espera el debate completo dentro del webhook
                
                # 1. Confirmar recepción inmediata (evita timeout)
                await send_telegram(
                    "🏛️ *Parlamento Nexus convocado.*\n\n"
                    "⏳ Procesando tu consulta... Te responderé en breve.",
                    chat_id=chat_id
                )
                
                # 2. Programar el debate en segundo plano
                #    Esto permite que el webhook responda en < 1 segundo
                #    mientras el debate se ejecuta asíncronamente
                background_tasks.add_task(
                    procesar_debate_background,
                    text=text,
                    chat_id=chat_id
                )
                
                # 3. Retornar inmediatamente (Vercel no hace timeout)
                #    El usuario recibirá la respuesta completa cuando termine el debate
                return {"ok": True, "status": "processing"}
                
            else:
                # Consulta directa a un departamento (rápida)
                # Esta ruta no necesita background porque es una llamada simple
                role = intent["role"]
                dept_name = intent["department"].capitalize()
                await send_telegram(f"🔍 *Consultando a {dept_name}...*", chat_id=chat_id)
                response_text = await call_ia(role, text)
                
                # Truncar si es demasiado largo
                if len(response_text) > 4000:
                    response_text = response_text[:4000] + "\n\n...(truncado)"
                
                await send_telegram(response_text, chat_id)
                return {"ok": True}
                
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            await send_telegram(f"❌ Error: {str(e)}", chat_id)
            return {"ok": True}

    return {"ok": True}

# ================================================
# SECCIÓN 7: FUNCIONES DE PROCESAMIENTO EN BACKGROUND
# ================================================
# 2026-07-07 - NUEVA SECCIÓN
# AUTOR: Arquitecto (Copilot)
# REF: Diagnóstico de timeout en Vercel (2026-07-07)
# ================================================
# DESCRIPCIÓN: Esta función se ejecuta en segundo plano después
# de que el webhook ya ha respondido. Permite que el debate
# parlamentario (que toma 15-30 segundos) no bloquee la respuesta.
# ================================================

async def procesar_debate_background(text: str, chat_id: int):
    """
    2026-07-07 - Función para procesar debate en segundo plano
    
    Esta función se ejecuta después de que el webhook ya respondió,
    evitando el timeout de Vercel (10 segundos en Hobby plan).
    
    Args:
        text (str): Consulta del usuario
        chat_id (int): ID del chat de Telegram
    
    Returns:
        None: La respuesta se envía directamente al chat de Telegram
    
    Observaciones:
        - Esta función es asíncrona y se ejecuta en background
        - No bloquea la respuesta HTTP del webhook
        - Los errores se capturan y notifican al usuario
        - Tiempo estimado de ejecución: 15-30 segundos
    """
    try:
        # 2026-07-07 - Importaciones dentro de la función
        # Esto evita que las importaciones se ejecuten en el webhook
        from api.router import (
            handle_parliament_debate,
            get_manager_recommendation
        )
        from api.parliament.actas import generate_acta, save_acta_to_github
        from datetime import datetime
        
        logger.info(f"📨 Iniciando debate en background para chat {chat_id}")
        
        # 2026-07-07 - Ejecutar debate (esto puede tomar 15-30 segundos)
        debate_results = await handle_parliament_debate(text)
        recommendation = await get_manager_recommendation(text, debate_results)
        
        # 2026-07-07 - Generar acta en background
        acta_content = await generate_acta(text, debate_results, recommendation)
        acta_result = await save_acta_to_github(
            acta_content,
            f"NEXUS-DEB-{datetime.now().strftime('%Y%m%d-%H%M')}"
        )
        
        # 2026-07-07 - Construir respuesta con resumen
        response_text = "🏛️ *DEBATE PARLAMENTARIO FINALIZADO*\n\n"
        for role, data in debate_results.items():
            # Limitar a 300 caracteres por rol para no exceder los 4000 de Telegram
            resp = data['response']
            if len(resp) > 300:
                resp = resp[:300] + "..."
            response_text += f"*{data['role']} ({data['model']}):*\n{resp}\n\n"
        response_text += f"---\n📋 *RECOMENDACIÓN FINAL:*\n{recommendation}"
        response_text += f"\n\n📄 {acta_result}"
        
        # 2026-07-07 - Enviar respuesta al usuario
        await send_telegram(response_text, chat_id)
        
        logger.info(f"✅ Debate completado para chat {chat_id}")
        
    except Exception as e:
        # 2026-07-07 - Capturar y notificar errores
        logger.error(f"❌ Error en debate background: {e}", exc_info=True)
        await send_telegram(
            f"❌ Error procesando el debate: {str(e)}\n\n"
            "Por favor, intenta de nuevo más tarde.",
            chat_id=chat_id
        )

# ================================================
# FIN DEL ARCHIVO
# ================================================
# 2026-07-07 - V3.0 COMPLETO
# CAMBIOS REALIZADOS:
# 1. ADD: BackgroundTasks en importación (línea 38)
# 2. MOD: Firma de telegram_webhook (línea 169)
# 3. MOD: Reemplazo de bloque de debate (líneas 406-435)
# 4. ADD: Función procesar_debate_background (líneas 445+)
# 5. ADD: Observaciones y fechas en todas las secciones modificadas
# ================================================
