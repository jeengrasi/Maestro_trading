import os
import httpx
import logging
import base64
from datetime import datetime
from .core import call_ia

logger = logging.getLogger(__name__)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "jeengrasi/Maestro_trading"
REDIS_URL = os.getenv("UPSTASH_REDIS_REST_URL")
REDIS_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

if REDIS_URL:
    try:
        import redis
        r = redis.from_url(f"{REDIS_URL}?password={REDIS_TOKEN}")
        logger.info("✅ Conexión a Redis establecida")
    except Exception as e:
        logger.error(f"❌ Error conectando a Redis: {e}")

async def generate_acta(message: str, responses: dict, recommendation: str) -> str:
    debate_id = f"NEXUS-DEB-{datetime.now().strftime('%Y%m%d-%H%M')}"
    context = f"ID: {debate_id}\nTema: {message}\n\n=== POSTURAS ===\n\n"
    for role, data in responses.items():
        context += f"--- {data['role']} ---\n{data['response']}\n\n"
    context += f"--- Gerente ---\n{recommendation}\n"
    context += "\nGenera el acta en Markdown."
    return await call_ia("secretario", context)

async def save_acta_to_github(acta_content: str, debate_id: str) -> dict:
    if not GITHUB_TOKEN:
        return {"status": "no_token"}
    
    filename = f"01-MEMORIA/DOCS/actas/{debate_id}.md"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
    content_base64 = base64.b64encode(acta_content.encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "message": f"Acta {debate_id}",
        "content": content_base64,
        "branch": "main"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=headers, json=payload, timeout=20.0)
            if response.status_code in (200, 201):
                logger.info(f"✅ Acta guardada en GitHub: {filename}")
                try:
                    if REDIS_URL and 'r' in locals():
                        key = f"doc:01-MEMORIA:DOCS:actas:{debate_id}"
                        r.hset(key, mapping={
                            "contenido": acta_content[:5000],
                            "ruta": filename,
                            "fecha_index": datetime.now().isoformat(),
                            "debate_id": debate_id
                        })
                        logger.info(f"✅ Acta guardada en Redis: {key}")
                except Exception as e:
                    logger.error(f"❌ Error guardando en Redis: {e}")
                return {"status": "success", "filename": filename}
            return {"status": "error", "code": response.status_code}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def indexar_acta(acta_content: str, debate_id: str) -> dict:
    if not REDIS_URL or 'r' not in locals():
        return {"status": "no_redis"}
    try:
        key = f"doc:01-MEMORIA:DOCS:actas:{debate_id}"
        r.hset(key, mapping={
            "contenido": acta_content[:5000],
            "ruta": f"01-MEMORIA/DOCS/actas/{debate_id}.md",
            "fecha_index": datetime.now().isoformat(),
            "debate_id": debate_id
        })
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
