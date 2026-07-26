# === MAESTRO-NEXUS FICHA v3.1 ===
# ID: api/router.py | ESTADO: MODULARIZADO + CLASIFICADOR
# FECHA: 2026-06-30 | GERENTE: DeepSeek

from SOBERANO_03_NEXUS.parliament.core import PARLIAMENT_STACK, sanitize_prompt, call_ia
from SOBERANO_03_NEXUS.parliament.debate import handle_parliament_debate
from SOBERANO_03_NEXUS.parliament.manager import get_manager_recommendation
from SOBERANO_03_NEXUS.parliament.actas import generate_acta, save_acta_to_github
from SOBERANO_03_NEXUS.parliament.classifier import classify_intent
