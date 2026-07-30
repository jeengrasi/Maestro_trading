# ==============================================================================
# ARCHIVO: utils.py
# MODULO: telegram
# DEPARTAMENTO: 03 - NEXUS (Telecomunicaciones)
# SISTEMA: MAESTRO-NEXUS
# ROL: El Mensajero Oficial
# MISIÓN: Traducir decisiones del sistema a mensajes de Telegram con formato Markdown.
# DEBERES: Respetar límite de 250 palabras, soportar botones inline, nunca fallar silenciosamente.
# PROHIBICIONES: Tomar decisiones de trading, almacenar datos localmente.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

import httpx
import logging
import os
from SOBERANO_03_NEXUS.config import Config

logger = logging.getLogger(__name__)

# [MOD-2026-07-27] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Implementar Message Chunking para evitar el truncamiento de respuestas 
#         largas que cumplen con la Norma EDVC v1.0 (Limite de Telegram: 4096 chars).
# REF: RESUMEN_ESTRATEGICO_FASES_1_Y_2.md (Fase 3, Tarea 3)

async def send_telegram_chunked(text: str, chat_id: int = None):
    """Envia un mensaje a Telegram, dividiendolo en chunks de max 3500 caracteres si es necesario."""
    target_id = chat_id or Config.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Dividir el texto en bloques de 3500 caracteres (margen de seguridad para Markdown)
    chunk_size = 3500
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    
    for i, chunk in enumerate(chunks):
        payload = {
            "chat_id": target_id, 
            "text": chunk, 
            "parse_mode": "Markdown"
        }
        # Indicador visual solo en el ultimo fragmento si hay multiples
        if len(chunks) > 1 and i == len(chunks) - 1:
            payload["text"] = chunk + "\n\n_(Fin del analisis)_"
            
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json=payload, timeout=10.0)
                r.raise_for_status()
                logger.info(f"Chunk {i+1}/{len(chunks)} enviado a Telegram.")
        except Exception as e:
            logger.error(f"Error enviando chunk {i+1} a Telegram: {e}")

# Mantener la funcion original por compatibilidad, redirigiendo a la nueva
async def send_telegram(text: str, chat_id: int = None, reply_markup: dict = None):
    await send_telegram_chunked(text, chat_id)
