# ==============================================================================
# ARCHIVO: router.py
# DEPARTAMENTO: 03 - NEXUS (Raíz)
# SISTEMA: MAESTRO-NEXUS
# ROL: Enrutador de Peticiones
# MISIÓN: Clasificar intenciones y dirigir el flujo al módulo correspondiente.
# DEBERES: Cumplir con la Constitución, no hardcodear credenciales, registrar errores.
# PROHIBICIONES: Violar las reglas transversales del Manifiesto de Roles.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

# === MAESTRO-NEXUS FICHA v3.1 ===
# ID: api/router.py | ESTADO: MODULARIZADO + CLASIFICADOR
# FECHA: 2026-06-30 | GERENTE: DeepSeek

from SOBERANO_03_NEXUS.parliament.core import PARLIAMENT_STACK, sanitize_prompt, call_ia
from SOBERANO_03_NEXUS.parliament.debate import handle_parliament_debate
from SOBERANO_03_NEXUS.parliament.manager import get_manager_recommendation
from SOBERANO_03_NEXUS.parliament.actas import generate_acta, save_acta_to_github
from SOBERANO_03_NEXUS.parliament.classifier import classify_intent
