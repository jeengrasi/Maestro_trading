import os, httpx, logging, base64
from datetime import datetime
from .core import call_ia

logger = logging.getLogger(__name__)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "jeengrasi/Maestro_trading"

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
    filename = f"docs/actas/{debate_id}.md"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
    content_base64 = base64.b64encode(acta_content.encode("utf-8")).decode("utf-8")
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Content-Type": "application/json", "Accept": "application/vnd.github+json"}
    payload = {"message": f"Acta {debate_id}", "content": content_base64, "branch": "main"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=headers, json=payload, timeout=20.0)
            if response.status_code in (200, 201):
                logger.info(f"Acta guardada: {filename}")
                return {"status": "success"}
            return {"status": "error", "code": response.status_code}
    except Exception as e:
        return {"status": "error", "message": str(e)}
