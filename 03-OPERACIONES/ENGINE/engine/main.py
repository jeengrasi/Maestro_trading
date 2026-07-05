import os, httpx, json, sys, asyncio
sys.path.insert(0, '.')
from api.parliament.core import call_ia
from api.parliament.classifier import classify_intent
from api.parliament.debate import handle_parliament_debate
from api.parliament.manager import get_manager_recommendation

redis_url = os.environ["UPSTASH_REDIS_REST_URL"]
redis_token = os.environ["UPSTASH_REDIS_REST_TOKEN"]
telegram_token = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id = os.environ["TELEGRAM_CHAT_ID"]

def send_telegram(text):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    httpx.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10)

async def procesar_mensajes():
    r = httpx.get(f"{redis_url}/keys/pending:*", headers={"Authorization": f"Bearer {redis_token}"})
    keys = r.json().get("result", [])
    
    for key in keys:
        r = httpx.get(f"{redis_url}/get/{key}", headers={"Authorization": f"Bearer {redis_token}"})
        msg = json.loads(r.json().get("result", "{}"))
        text = msg.get("text", "")
        
        if text:
            send_telegram("🏛️ *Parlamento Nexus debatiendo...*")
            intent = classify_intent(text)
            
            if intent["confidence"] >= 1:
                debate_results = await handle_parliament_debate(text)
                recommendation = await get_manager_recommendation(text, debate_results)
                response = f"🏛️ *DEBATE PARLAMENTARIO*\n\n"
                for role, data in debate_results.items():
                    response += f"*{data['role']}:*\n{data['response']}\n\n"
                response += f"---\n📋 *RECOMENDACIÓN FINAL:*\n{recommendation}"
            else:
                role = intent["role"]
                response = await call_ia(role, text)
            
            if len(response) > 4000:
                response = response[:4000] + "\n\n...(truncado)"
            
            send_telegram(response)
        
        httpx.delete(f"{redis_url}/del/{key}", headers={"Authorization": f"Bearer {redis_token}"})

if __name__ == "__main__":
    asyncio.run(procesar_mensajes())
