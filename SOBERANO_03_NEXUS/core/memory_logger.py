# ==============================================================================
# ARCHIVO: memory_logger.py
# MODULO: core
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Registrar decisiones y uso de herramientas en la Bitácora Soberana.
#            Cumple el Art. 5: "La memoria es el sistema, no la memoria de la IA".
# ==============================================================================
import os
import datetime

def registrar_en_bitacora(chat_id: str, accion: str, herramientas_usadas: list, resultado_resumen: str):
    """
    Escribe una entrada estructurada en la bitácora del sistema.
    """
    bitacora_path = "SOBERANO_01_MEMORIA/bitacora.md"
    
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
