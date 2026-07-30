# ==============================================================================
# ARCHIVO: github_rag.py
# MODULO: parliament
# DEPARTAMENTO: 03 - NEXUS (Parlamento)
# SISTEMA: MAESTRO-NEXUS
# ROL: El Bibliotecario RAG
# MISIÓN: Consultar archivos de gobierno en GitHub cuando el usuario pregunta por normas.
# DEBERES: Leer CONSTITUCION.md y NORMAS.md vía API de GitHub, devolver contexto normativo estructurado.
# PROHIBICIONES: Modificar archivos de gobierno, ejecutar trading.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

# ==============================================================================
# ARCHIVO: github_rag.py
# MODULO: parliament
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Obtener contexto de gobierno (Normas, Constitución) desde GitHub API
#            para inyectar en los prompts de la IA y evitar alucinaciones.
# ULTIMA MODIFICACION: 2026-07-29
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# ==============================================================================
# [MOD-2026-07-29] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Implementar RAG básico con GitHub API para respuestas normativas.
# REF: Fase 11.1 - Inteligencia Superior con contexto real.

import os
import httpx
import logging

logger = logging.getLogger(__name__)

async def obtener_contexto_gobierno() -> str:
    """
    Descarga las normas y constitución desde GitHub API para usar como contexto.
    Retorna un string con el contenido o un mensaje de error.
    """
    gh_token = os.getenv("GITHUB_TOKEN")
    repo = "jeengrasi/Maestro_trading"
    branch = "soberano-v1"
    
    if not gh_token:
        logger.warning("GITHUB_TOKEN no configurado para RAG")
        return "ERROR: Sin token de GitHub."
    
    headers = {
        "Authorization": f"Bearer {gh_token}",
        "Accept": "application/vnd.github.v3.raw", # Solicita el contenido raw, no el JSON con base64
        "User-Agent": "Nexus-RAG"
    }
    
    archivos_clave = [
        f"SOBERANO_00_GOBIERNO/NORMAS.md",
        f"SOBERANO_00_GOBIERNO/CONSTITUCION.md"
    ]
    
    contexto_total = "📜 CONTEXTO DE GOBIERNO NEXUS (OBLIGATORIO PARA RESPONDER):\n\n"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for archivo in archivos_clave:
            url = f"https://api.github.com/repos/{repo}/contents/{archivo}?ref={branch}"
            try:
                r = await client.get(url, headers=headers)
                if r.status_code == 200:
                    # Con el header 'application/vnd.github.v3.raw', el contenido viene directo
                    contexto_total += f"--- {archivo} ---\n{r.text[:1500]}...\n\n" # Limitamos a 1500 chars para no saturar el prompt
                else:
                    contexto_total += f"--- {archivo} ---\n[No accesible: HTTP {r.status_code}]\n\n"
            except Exception as e:
                logger.error(f"Error leyendo {archivo}: {e}")
                contexto_total += f"--- {archivo} ---\n[Error de lectura]\n\n"
    
    return contexto_total
