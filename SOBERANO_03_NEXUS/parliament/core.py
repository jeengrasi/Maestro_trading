import os
import logging
from datetime import datetime
from SOBERANO_03_NEXUS.providers.mistral import call_mistral

logger = logging.getLogger(__name__)

PARLIAMENT_STACK = {
    "gerente": "Mistral (Decisión final, estrategia)",
    "analista": "Mistral (Análisis técnico)",
    "auditor": "Mistral (Validación de riesgos)",
    "estratega": "Mistral (Análisis financiero)",
    "secretario": "Mistral (Generación de actas)"
}

def leer_contexto_obligatorio() -> str:
    bitacora_path = "SOBERANO_01_MEMORIA/bitacora.md"
    try:
        if not os.path.exists(bitacora_path):
            return "No hay historial previo disponible."
        with open(bitacora_path, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            return "".join(lineas[-30:]) if len(lineas) > 30 else "".join(lineas)
    except Exception as e:
        logger.error(f"Error leyendo bitácora: {e}")
        return "Error al leer historial."

def escribir_en_bitacora(accion: str, resultado: str):
    bitacora_path = "SOBERANO_01_MEMORIA/bitacora.md"
    try:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nuevo_registro = f"\n- **{fecha}** | **{accion}** | {resultado[:150]}...\n"
        with open(bitacora_path, "a", encoding="utf-8") as f:
            f.write(nuevo_registro)
    except Exception as e:
        logger.error(f"Error escribiendo en bitácora: {e}")

def sanitize_prompt(prompt: str) -> str:
    return prompt.strip()

async def call_ia(role: str, message: str) -> str:
    contexto = leer_contexto_obligatorio()
    
    # [MOD-2026-07-27] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
    # MOTIVO: Integrar Norma EDVC v1.0 en el system prompt para garantizar trazabilidad.
    # REF: SOBERANO_00_GOBIERNO/NORMAS.md
    edvc_instruction = """

🚨 INSTRUCCION CRITICA (NORMA EDVC v1.0):
Si en tu respuesta debes generar o modificar codigo, DEBES aplicar estrictamente las 4 capas del estandar EDVC:
1. CAPA 1: Cedula de Identidad (Encabezado con ARCHIVO, SISTEMA, PROPOSITO, FECHA, AUTOR, VALIDADOR, AUDITORIA).
2. CAPA 2: Contexto de Seccion (Explicar el PORQUE arquitectonico antes de bloques logicos).
3. CAPA 3: La Cicatriz Quirurgica (Etiqueta [MOD-YYYY-MM-DD] [AUTOR] [VALIDADOR] MOTIVO: REF: antes de cambios criticos).
4. CAPA 4: Changelog Vivo (Registro cronologico inverso al final del archivo).
PROHIBIDO: Comentar cada linea individual o dejar codigo comentado sin etiqueta [DEPRECATED].
Si no cumples, tu respuesta sera rechazada por el Auditor de Riesgos.
"""
    
    system_prompts = {
        "gerente": f"Eres el Gerente General del Parlamento Nexus. Toma decisiones estratégicas finales.\nContexto histórico:\n{contexto}\nResponde de forma concisa y profesional.",
        "analista": f"Eres el Analista Técnico. Analiza datos y tendencias.\nContexto:\n{contexto}\nSé preciso y basado en datos.",
        "auditor": f"Eres el Auditor de Riesgos (Art. 14: máx 1% riesgo, VIX máx 20).\nContexto:\n{contexto}\nEvalúa riesgos y veta si es necesario.",
        "estratega": f"Eres el Estratega de Mercado. Analiza oportunidades de inversión.\nContexto:\n{contexto}\nFundamenta tus recomendaciones.",
        "secretario": f"Eres el Secretario. Genera actas y documentos claros.\nContexto:\n{contexto}"
    }
    
    system_prompt = system_prompts.get(role, system_prompts["gerente"]) + edvc_instruction
    
    logger.info(f"🧠 Llamando a Mistral para rol: {role}")
    respuesta = await call_mistral("mistral-small-latest", system_prompt, message)
    
    escribir_en_bitacora(f"CONSULTA_{role.upper()}", f"P: {message[:50]} | R: {respuesta[:50]}")
    
    return respuesta
