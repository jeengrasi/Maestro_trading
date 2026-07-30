# ==============================================================================
# ARCHIVO: memory_logger.py
# MODULO: core
# DEPARTAMENTO: 01 - MEMORIA
# SISTEMA: MAESTRO-NEXUS
# ROL: El Escribano Oficial
# MISIÓN: Registrar todas las decisiones del sistema en la Bitácora Soberana (bitacora.md).
# DEBERES: Escribir interacciones con fecha/hora, fallback a Redis en Vercel, cumplir formato EDVC.
# PROHIBICIONES: Tomar decisiones de trading, modificar archivos de gobierno, enviar mensajes a Telegram.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

# ==============================================================================
# ARCHIVO: memory_logger.py
# MODULO: core
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Registrar decisiones en la Bitácora Soberana.
#            Compatible con Vercel (Read-Only File System) usando fallback a Redis.
# ==============================================================================
import os
import datetime
import logging

logger = logging.getLogger(__name__)

def registrar_en_bitacora(chat_id: str, accion: str, herramientas_usadas: list, resultado_resumen: str, redis_client=None):
    """
    Escribe una entrada estructurada en la bitácora del sistema.
    Si el entorno es de solo lectura (ej. Vercel), hace fallback seguro a Redis.
    """
    bitacora_path = "SOBERANO_01_MEMORIA/bitacora.md"
    
    try:
        os.makedirs("SOBERANO_01_MEMORIA", exist_ok=True)
        
        if not os.path.exists(bitacora_path):
            with open(bitacora_path, "w", encoding="utf-8") as f:
                f.write("# 📝 BITÁCORA SOBERANA DEL SISTEMA MAESTRO-NEXUS\n\n")
                f.write("*La memoria es el sistema, no la memoria de la IA. (Art. 5)*\n\n---\n\n")
        
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        herramientas_str = ", ".join(herramientas_usadas) if herramientas_usadas else "Ninguna"
        
        entrada = f"""
---
id: LOG-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}
fecha: {fecha}
chat_id: {chat_id}
accion: {accion}
herramientas: [{herramientas_str}]
---
**[RESUMEN DE LA INTERACCIÓN]**
{resultado_resumen}

---
"""
        with open(bitacora_path, "a", encoding="utf-8") as f:
            f.write(entrada)
            
    except (OSError, PermissionError) as e:
        # Fallback para entornos serverless de solo lectura (Vercel)
        logger.warning(f"Entorno de solo lectura detectado. Fallback a Redis: {e}")
        if redis_client:
            try:
                redis_key = f"bitacora_fallback:{chat_id}"
                entry = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {accion} | {resultado_resumen[:100]}"
                redis_client.lpush(redis_key, entry)
                redis_client.expire(redis_key, 86400) # 24 horas
            except Exception as redis_e:
                logger.error(f"Fallo en fallback de Redis: {redis_e}")
