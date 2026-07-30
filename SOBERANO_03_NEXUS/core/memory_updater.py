# ==============================================================================
# ARCHIVO: memory_updater.py
# DEPARTAMENTO: 03 - NEXUS (Núcleo)
# SISTEMA: MAESTRO-NEXUS
# ROL: Actualizador de Bitácora
# MISIÓN: Sincronizar estados locales con la bitácora soberana en GitHub.
# DEBERES: Cumplir con la Constitución, no hardcodear credenciales, registrar errores.
# PROHIBICIONES: Violar las reglas transversales del Manifiesto de Roles.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

# ==============================================================================
# ARCHIVO: memory_updater.py
# MODULO: core
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Automatizar la actualización de ROADMAP.md y bitacora.md 
#            cumpliendo estrictamente con la Norma EDVC v1.0 y Art. 5/11.
# ULTIMA MODIFICACION: 2026-07-29
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# ==============================================================================
# [MOD-2026-07-29] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Reparar la falla crítica de alimentación manual de memoria del sistema.
# REF: Constitución v7.1 (Art. 5: La Memoria es el Sistema, Art. 11: Bitácora inmutable).

import os
import datetime
import logging

logger = logging.getLogger(__name__)

def generar_entrada_edvc(accion: str, detalles: str) -> str:
    """Genera una entrada de bitácora con formato EDVC v1.0 obligatorio."""
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fecha_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    entrada = f"""
---
id: AUTO-{fecha_str.replace('-', '')}-{hash(accion) % 10000}
date: {fecha_str}
type: actualizacion_automatica
status: REGISTRADO
author: Sistema_Automata (Qwen)
validator: Director (JEISSON_01)
tags: [automatizacion, memoria, edvc_v1.0]
---

# 📝 REGISTRO AUTOMÁTICO DE SISTEMA

**[CONTEXTO]**
El sistema ha detectado y procesado automáticamente la siguiente acción para mantener la integridad de la memoria.

**[DETALLES DE LA ACCIÓN]**
{detalles}

**[CICATRIZ QUIRURGICA]**
[MOD-{fecha_str}] [SISTEMA] [AUTOMATA] Actualizacion de memoria por evento: {accion}

**[CHANGELOG VIVO]**
- {ahora}: Entrada de bitácora generada automáticamente.
- {ahora}: Estado del sistema sincronizado con repositorio.
"""
    return entrada.strip()

def actualizar_bitacora(accion: str, detalles: str):
    """Añade la entrada EDVC al final de la bitácora principal."""
    bitacora_path = "SOBERANO_01_MEMORIA/bitacora.md"
    try:
        entrada = generar_entrada_edvc(accion, detalles)
        with open(bitacora_path, "a", encoding="utf-8") as f:
            f.write("\n\n" + entrada + "\n")
        logger.info(f"✅ Bitácora actualizada automáticamente: {accion}")
        return True
    except Exception as e:
        logger.error(f"❌ Fallo al actualizar bitácora: {e}")
        return False

def actualizar_roadmap():
    """Escanea módulos existentes y actualiza el estado del ROADMAP.md."""
    roadmap_path = "SOBERANO_01_MEMORIA/ROADMAP.md"
    if not os.path.exists(roadmap_path):
        return False
    
    with open(roadmap_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Lógica simple de detección de fases por existencia de archivos clave
    actualizaciones = []
    if os.path.exists("SOBERANO_03_NEXUS/trading/risk_manager.py") and "[FASE 9: RIESGO Y PODA]" in content:
        content = content.replace("[FASE 9: RIESGO Y PODA] -> PENDIENTE", "[FASE 9: RIESGO Y PODA] -> COMPLETADA ✅")
        actualizaciones.append("Fase 9 marcada como completada")
        
    if os.path.exists("SOBERANO_03_NEXUS/core/contralor.py") and "[FASE 10: CONTRALOR TRANSVERSAL]" in content:
        content = content.replace("[FASE 10: CONTRALOR TRANSVERSAL] -> PENDIENTE", "[FASE 10: CONTRALOR TRANSVERSAL] -> COMPLETADA ✅")
        actualizaciones.append("Fase 10 marcada como completada")
        
    if os.path.exists("SOBERANO_03_NEXUS/core/memory_updater.py") and "[FASE 11: AUTOMATIZACION DE MEMORIA]" in content:
        content = content.replace("[FASE 11: AUTOMATIZACION DE MEMORIA] -> PENDIENTE", "[FASE 11: AUTOMATIZACION DE MEMORIA] -> COMPLETADA ✅")
        actualizaciones.append("Fase 11 marcada como completada")

    if actualizaciones:
        with open(roadmap_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"✅ ROADMAP actualizado: {', '.join(actualizaciones)}")
        actualizar_bitacora("ACTUALIZACION_ROADMAP", ", ".join(actualizaciones))
        return True
    
    return False

if __name__ == "__main__":
    print("🔄 Ejecutando sincronización automática de memoria...")
    actualizar_roadmap()
    print("✅ Proceso de memoria automática finalizado.")
