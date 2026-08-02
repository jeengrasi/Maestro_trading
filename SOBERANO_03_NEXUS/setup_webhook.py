#!/usr/bin/env python3
import os
import httpx

def configurar_webhook():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    railway_url = os.getenv("RAILWAY_PUBLIC_DOMAIN", "maestrotrading-production-c2db.up.railway.app")
    
    if not railway_url.startswith("http"):
        railway_url = f"https://{railway_url}"
    
    webhook_url = f"{railway_url}/webhook/telegram"
    print(f"Configurando webhook en: {webhook_url}")
    
    try:
        httpx.get(f"https://api.telegram.org/bot{bot_token}/deleteWebhook")
        response = httpx.get(f"https://api.telegram.org/bot{bot_token}/setWebhook", params={"url": webhook_url})
        if response.json().get("ok"):
            print("✅ Webhook configurado exitosamente!")
        else:
            print(f"❌ Error: {response.json()}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    configurar_webhook()
