# ==============================================================================
# ARCHIVO: webhook.py
# MODULO: telegram
# DEPARTAMENTO: 03 - NEXUS (Telecomunicaciones)
# SISTEMA: MAESTRO-NEXUS
# ROL: Webhook de Telegram
# MISIÓN: Recibir comandos de Telegram, verificar seguridad y delegar al
#         CommandProcessor para generar respuestas.
# DEBERES: Cumplir con la Constitución, verificar chat_id, responder en <5 seg.
# PROHIBICIONES: Ejecutar trading, modificar archivos de gobierno.
# ULTIMA MODIFICACION: 2026-08-01
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: Constitución v7.1 (Art. 1, 12), Fase 1.2
# ==============================================================================

import os
import logging
from fastapi import APIRouter, Request, HTTPException
from upstash_redis import Redis
from SOBERANO_03_NEXUS.config import Config
from SOBERANO_03_NEXUS.telegram.commands import CommandProcessor
from SOBERANO_03_NEXUS.telegram.utils import send_telegram

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """Endpoint para recibir webhooks de Telegram."""
    try:
        # Inicializar dependencias
        config = Config()
        redis_client = Redis(url=config.UPSTASH_REDIS_REST_URL, token=config.UPSTASH_REDIS_REST_TOKEN)
        command_processor = CommandProcessor(redis_client)
        
        # Parsear payload de Telegram
        data = await request.json()
        
        # Verificar que sea un mensaje
        if "message" not in data:
            return {"ok": True}
        
        message = data["message"]
        chat_id = message["chat"]["id"]
        
        # VERIFICACIÓN DE SEGURIDAD: Solo el Director puede ejecutar comandos
        if not command_processor.verificar_autorizacion(chat_id):
            logger.warning(f"Intento de acceso no autorizado desde chat_id: {chat_id}")
            return {"ok": True}  # Responder 200 para que Telegram no reintente
        
        # Extraer comando
        text = message.get("text", "")
        if not text.startswith("/"):
            return {"ok": True}
        
        # Parsear comando y argumentos
        parts = text.split()
        comando = parts[0].split("@")[0]  # Remover @bot_name si existe
        args = parts[1:] if len(parts) > 1 else []
        
        logger.info(f"Comando recibido: {comando} {args}")
        
        # Procesar comando
        respuesta = command_processor.procesar_comando(comando, args)
        
        # Enviar respuesta a Telegram
        await send_telegram(respuesta, chat_id=chat_id)
        
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"Error en webhook de Telegram: {e}")
        # Responder 200 para evitar reintentos de Telegram
        return {"ok": True}
