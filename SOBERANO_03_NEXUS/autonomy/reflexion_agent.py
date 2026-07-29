# ==============================================================================
# ARCHIVO: reflexion_agent.py
# MODULO: autonomy
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Analizar bloqueos del Risk Manager, generar reflexión post-mortem 
#            y crear Issues en GitHub para propuesta de mejora normativa.
# ULTIMA MODIFICACION: 2026-07-29
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# ==============================================================================
# [MOD-2026-07-29] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Fase 12.3 - Cerrar el ciclo de aprendizaje autónomo del sistema.
# REF: Constitución v7.1 (Art. 5: La Memoria es el Sistema), Norma EDVC v1.0.

import os
import json
import httpx
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def generar_reflexion_y_propuesta(redis_client) -> dict:
    """
    Lee los últimos bloqueos de Redis, pide a Mistral un análisis post-mortem 
    y crea un Issue en GitHub para la ratificación del Director.
    """
    try:
        # 1. Obtener últimos 5 bloqueos del Risk Manager
        bloqueos = redis_client.lrange("reflexion:bloqueos", 0, 4)
        if not bloqueos:
            return {"status": "skipped", "message": "No hay bloqueos recientes para analizar."}
        
        bloqueos_text = "\n".join([b.decode() if isinstance(b, bytes) else str(b) for b in bloqueos])
        
        # 2. Preparar prompt para Mistral (Estricto formato EDVC)
        prompt = f"""
Analiza los siguientes bloqueos del Risk Manager en el sistema Maestro-Nexus.
Tu objetivo es identificar patrones y proponer UN ajuste concreto a las normas (ej: ajustar umbral de VIX, agregar un activo a lista negra temporal, etc.).

BLOQUEOS RECIENTES:
{bloqueos_text}

RESponde EXCLUSIVAMENTE en este formato Markdown (Norma EDVC v1.0):
### 📊 ANÁLISIS POST-MORTEM
- **Patrón Detectado:** [1 línea]
- **Causa Raíz:** [1 línea]

### 💡 PROPUESTA DE MEJORA NORMATIVA
- **Acción Sugerida:** [Ej: "Reducir MAX_VIX de 20 a 18 para activos tecnológicos"]
- **Justificación:** [1-2 líneas basadas en los datos]

### ⚠️ RIESGO DE NO ACTUAR
- [1 línea sobre la consecuencia de ignorar esto]
"""
        
        # 3. Llamar a Mistral
        api_key = os.getenv("MISTRAL_API_KEY")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "mistral-small-latest",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload)
            
        if r.status_code != 200:
            return {"status": "error", "message": f"Error en Mistral: {r.status_code}"}
            
        analisis = r.json()["choices"][0]["message"]["content"]
        
        # 4. Crear Issue en GitHub
        gh_token = os.getenv("GITHUB_TOKEN")
        repo = "jeengrasi/Maestro_trading"
        gh_headers = {
            "Authorization": f"Bearer {gh_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Nexus-Reflexion"
        }
        issue_payload = {
            "title": f"[PROPUESTA-MEJORA] Reflexión Post-Mortem: {datetime.now().strftime('%Y-%m-%d')}",
            "body": f"🤖 **Generado automáticamente por el Motor de Reflexión de Nexus**\n\nEl sistema ha detectado patrones recurrentes de bloqueo. Se solicita la revisión y ratificación del Director (JEISSON_01).\n\n---\n\n{analisis}\n\n---\n\n✅ *Para aprobar:* Comenta 'APROBADO' y el sistema aplicará el cambio.\n❌ *Para rechazar:* Comenta 'RECHAZADO' y el sistema archivará la propuesta.",
            "labels": ["propuesta-mejora", "reflexion-ia", "pendiente-ratificacion"]
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client_gh:
            r_gh = await client_gh.post(f"https://api.github.com/repos/{repo}/issues", headers=gh_headers, json=issue_payload)
            
        if r_gh.status_code in [201, 200]:
            issue_url = r_gh.json().get("html_url")
            # Limpiar la cola de bloqueos procesados
            redis_client.ltrim("reflexion:bloqueos", 5, -1)
            return {"status": "success", "message": f"Issue creado exitosamente: {issue_url}"}
        else:
            return {"status": "error", "message": f"Error creando Issue: {r_gh.status_code} - {r_gh.text[:100]}"}
            
    except Exception as e:
        logger.error(f"❌ Error en reflexion_agent: {e}")
        return {"status": "error", "message": str(e)[:100]}
