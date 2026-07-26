import httpx, logging, os
from SOBERANO_03_NEXUS.config import Config
logger = logging.getLogger(__name__)

async def send_telegram(text: str, chat_id: int = None):
    target_id = chat_id or Config.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": target_id, "text": text, "parse_mode": "Markdown"}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        return r.json().get("result", {})
