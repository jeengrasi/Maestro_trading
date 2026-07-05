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
from api.config import Config
from api.telegram.utils import send_telegram

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

redis = Redis(url=os.getenv("UPSTASH_REDIS_REST_URL"), token=os.getenv("UPSTASH_REDIS_REST_TOKEN"))
_alpaca_client = None

def get_alpaca_client():
    global _alpaca_client
    if _alpaca_client is None:
        _alpaca_client = TradingClient(Config.ALPACA_API_KEY, Config.ALPACA_SECRET_KEY, paper=Config.ALPACA_PAPER)
    return _alpaca_client

def bootstrap_nexus_memory(redis_client: Redis):
    try:
        tg_id = redis_client.get("telegram:group_id")
        feat_parliament = redis_client.get("feature:parliament")
        if not tg_id or not feat_parliament:
            manifest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "NEXUS_MANIFEST.json")
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                state = manifest.get("state_declarative", {})
                if not tg_id:
                    redis_client.set("telegram:group_id", "6444278889")
                if not feat_parliament:
                    redis_client.set("feature:parliament", "0")
                redis_client.set("risk:max_vix", str(state.get("risk_management", {}).get("max_vix", "20.0")))
                redis_client.set("nexus:state:last_recovery", datetime.now().isoformat())
                logger.info("Redis auto-hidratado.")
    except Exception as e:
        logger.error(f"Error memoria: {e}", exc_info=True)

@app.get("/")
async def root():
    return {"status": "running", "system": "Maestro-Nexus"}

@app.get("/health")
async def health():
    start = datetime.now()
    try:
        r = await asyncio.wait_for(asyncio.to_thread(redis.ping), timeout=2.0)
        redis_ok = (r == "PONG" or r is True)
    except:
        redis_ok = False
    return {"status": "ok" if redis_ok else "degraded", "redis": redis_ok, "latency_ms": round((datetime.now() - start).total_seconds() * 1000, 2)}

@app.get("/webhook")
async def webhook_verification():
    return {"status": "ok"}

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

    if text == "/chatid":
        await send_telegram(f"Chat ID: `{chat_id}`\nEsperado: `{authorized_chat}`", chat_id=chat_id)
        return {"ok": True}

    if text == "/balance":
        acc = get_alpaca_client().get_account()
        modo = "🧪 PAPER" if Config.ALPACA_PAPER else "💰 REAL"
        await send_telegram(f"📊 *CUENTA ALPACA ({modo})*\n\n💵 *Equity:* ${float(acc.equity):,.2f}\n💸 *Buying Power:* ${float(acc.buying_power):,.2f}", chat_id=chat_id)
        return {"ok": True}

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
            f"/stop - Pausar el sistema",
            chat_id=chat_id
        )
        return {"ok": True}

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

    if text == "/stop":
        await send_telegram("🛑 *EMERGENCIA ACTIVADA*\n\nSistema pausado. Revisar logs.", chat_id=chat_id)
        return {"ok": True}

    # ================================================
    # COMANDO: /actualizar_bitacora
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
            await send_telegram(f"❌ Error: {str(e)}", chat_id=chat_id)
            return {"ok": True}

    if text and not text.startswith("/"):
        try:
            from api.router import handle_parliament_debate, get_manager_recommendation, classify_intent, call_ia
            from api.parliament.actas import generate_acta, save_acta_to_github
            
            intent = classify_intent(text)
            if intent["confidence"] >= 1:
                await send_telegram("🏛️ *Parlamento Nexus convocado.*\n\nLas IAs están debatiendo...", chat_id=chat_id)
                debate_results = await handle_parliament_debate(text)
                recommendation = await get_manager_recommendation(text, debate_results)
                response_text = "🏛️ *DEBATE PARLAMENTARIO*\n\n"
                for role, data in debate_results.items():
                    response_text += f"*{data['role']} ({data['model']}):*\n{data['response']}\n\n"
                response_text += f"---\n📋 *RECOMENDACIÓN FINAL:*\n{recommendation}"
                acta_content = await generate_acta(text, debate_results, recommendation)
                await save_acta_to_github(acta_content, f"NEXUS-DEB-{datetime.now().strftime('%Y%m%d-%H%M')}")
            else:
                role = intent["role"]
                dept_name = intent["department"].capitalize()
                await send_telegram(f"🔍 *Consultando a {dept_name}...*", chat_id=chat_id)
                response_text = await call_ia(role, text)
            
            if len(response_text) > 4000:
                response_text = response_text[:4000] + "\n\n...(truncado)"
            await send_telegram(response_text, chat_id)
            return {"ok": True}
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            await send_telegram(f"❌ Error: {str(e)}", chat_id)
            return {"ok": True}

    return {"ok": True}
