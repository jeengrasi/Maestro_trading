# === MAESTRO-NEXUS FICHA v3.0 ===
# ID: api/router.py | ESTADO: MODULARIZADO
# FECHA: 2026-06-30 | GERENTE: DeepSeek
# Este archivo ahora importa de api.parliament

from api.parliament.core import PARLIAMENT_STACK, sanitize_prompt, call_ia
from api.parliament.debate import handle_parliament_debate
from api.parliament.manager import get_manager_recommendation
from api.parliament.actas import generate_acta, save_acta_to_github
