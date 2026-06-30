import os, httpx, json, base64

redis_url = os.environ["UPSTASH_REDIS_REST_URL"]
redis_token = os.environ["UPSTASH_REDIS_REST_TOKEN"]
groq_key = os.environ["GROQ_API_KEY"]
github_token = os.environ["GITHUB_TOKEN"]

keys_url = f"{redis_url}/keys/debate:*"
r = httpx.get(keys_url, headers={"Authorization": f"Bearer {redis_token}"})
keys = r.json().get("result", [])

for key in keys:
    get_url = f"{redis_url}/get/{key}"
    r = httpx.get(get_url, headers={"Authorization": f"Bearer {redis_token}"})
    debate = json.loads(r.json().get("result", "{}"))
    
    groq_url = "https://api.groq.com/openai/v1/chat/completions"
    context = f"Genera un acta Markdown:\nTema: {debate.get('tema','')}\nResultados: {json.dumps(debate.get('resultados',{}))}\nRecomendación: {debate.get('recomendacion','')}"
    
    r = httpx.post(groq_url,
        headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
        json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": context}]},
        timeout=30
    )
    
    if r.status_code == 200:
        acta = r.json()["choices"][0]["message"]["content"]
        debate_id = key.split(":")[-1]
        filename = f"docs/actas/NEXUS-DEB-{debate_id}.md"
        
        content_b64 = base64.b64encode(acta.encode()).decode()
        github_url = f"https://api.github.com/repos/jeengrasi/Maestro_trading/contents/{filename}"
        httpx.put(github_url,
            headers={"Authorization": f"Bearer {github_token}", "Content-Type": "application/json"},
            json={"message": f"Acta {debate_id}", "content": content_b64, "branch": "main"}
        )
        
        httpx.delete(f"{redis_url}/del/{key}", headers={"Authorization": f"Bearer {redis_token}"})
        print(f"✅ Acta {debate_id} generada.")
