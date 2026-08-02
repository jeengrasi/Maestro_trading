import os
import httpx
import logging

logger = logging.getLogger(__name__)

async def send_telegram(message: str, chat_id: int):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Diagnóstico seguro: solo mostramos la longitud del token, nunca el token real
    if not token or len(token.strip()) < 40:
        logger.error("❌ CRÍTICO: TELEGRAM_BOT_TOKEN no está configurada, está vacía o es inválida.")
        logger.error(f"   Longitud detectada: {len(token) if token else 0} caracteres.")
        return
        
    logger.info(f"🔑 Token cargado correctamente. Longitud: {len(token)} caracteres.")
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            logger.info(f"✅ Mensaje enviado exitosamente a chat_id: {chat_id}")
    except httpx.HTTPError as e:
        logger.error(f"❌ Error HTTP enviando a Telegram: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"   Respuesta cruda de Telegram: {e.response.text}")
    except Exception as e:
        logger.error(f"❌ Error inesperado enviando a Telegram: {e}")
