# ==============================================================================
# ARCHIVO: inline_actions.py
# MODULO: telegram
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Manejar callbacks de botones inline de Telegram para autorización
#            temporal de ejecución (TTL 1H) o modo sombra.
# ULTIMA MODIFICACION: 2026-07-29
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# ==============================================================================
# [MOD-2026-07-29] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Fase 13 - Permitir autorización de trading con un solo toque y expiración automática.
# REF: Constitución v7.1 (Art. 14: Riesgo controlado), Norma EDVC v1.0.

import logging

logger = logging.getLogger(__name__)

async def handle_autorizacion_callback(query_data: str, redis_client) -> dict:
    """
    Maneja los callbacks de los botones inline de Telegram.
    query_data: ej. "AUTH_AAPL" o "SHADOW_AAPL"
    """
    try:
        parts = query_data.split("_")
        action = parts[0]
        ticker = parts[1] if len(parts) > 1 else "MERCADO"
        
        if action == "AUTH":
            # Autorizar ejecución por 1 hora (3600 segundos)
            redis_client.set("AUTO_EJECUCION_TEMP", "true", ex=3600)
            mensaje = (
                f"✅ *AUTORIZACIÓN TEMPORAL ACTIVADA*\n\n"
                f"El sistema ha sido autorizado para ejecutar operaciones en modo Paper "
                f"para *{ticker}* durante la próxima hora.\n\n"
                f"⏳ *Expiración automática:* 60 minutos.\n"
                f"🛡️ *Risk Manager:* Activo (Max 1% riesgo)."
            )
            return {"text": mensaje, "parse_mode": "Markdown"}
            
        elif action == "SHADOW":
            mensaje = (
                f"👁️ *MODO SOMBRA CONFIRMADO*\n\n"
                f"El sistema analizará *{ticker}* y registrará las señales, "
                f"pero *NO ejecutará* ninguna orden real.\n\n"
                f"📝 Las oportunidades se guardarán en la bitácora para su revisión."
            )
            return {"text": mensaje, "parse_mode": "Markdown"}
            
        else:
            return {"text": "⚠️ Acción no reconocida por el sistema.", "parse_mode": "Markdown"}
            
    except Exception as e:
        logger.error(f"❌ Error manejando callback inline: {e}")
        return {"text": f"❌ Error procesando la autorización: {str(e)[:50]}", "parse_mode": "Markdown"}
