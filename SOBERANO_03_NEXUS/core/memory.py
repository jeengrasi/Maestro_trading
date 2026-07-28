# ==============================================================================
# ARCHIVO: memory.py
# MODULO: core
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Gestión de memoria, inicialización de estado y persistencia de contexto.
# ULTIMA MODIFICACION: 2026-07-28
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# ==============================================================================
# [MOD-2026-07-28] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Extraer lógica de inicialización de memoria de index.py (Fase 9.1).
# REF: Principio de Separación de Responsabilidades.

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def bootstrap_nexus_memory(redis_client) -> None:
    """
    Inicializa y verifica el estado de la memoria en Redis.
    Si faltan claves críticas, las hidrata desde el manifiesto del sistema.
    """
    try:
        tg_id = redis_client.get("telegram:group_id")
        feat_parliament = redis_client.get("feature:parliament")
        
        if not tg_id or not feat_parliament:
            manifest_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "NEXUS_MANIFEST.json"
            )
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                state = manifest.get("state_declarative", {})
                
                if not tg_id:
                    redis_client.set("telegram:group_id", "6444278889")
                if not feat_parliament:
                    redis_client.set("feature:parliament", "0")
                
                redis_client.set(
                    "risk:max_vix",
                    str(state.get("risk_management", {}).get("max_vix", "20.0"))
                )
                redis_client.set(
                    "nexus:state:last_recovery",
                    datetime.now().isoformat()
                )
                logger.info("✅ Redis auto-hidratado exitosamente desde NEXUS_MANIFEST.json")
    except Exception as e:
        logger.error(f"❌ Error en bootstrap de memoria: {e}", exc_info=True)
