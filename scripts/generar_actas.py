import os, httpx, json, base64

redis_url = os.environ["UPSTASH_REDIS_REST_URL"]
redis_token = os.environ["UPSTASH_REDIS_REST_TOKEN"]
github_token = os.environ["GITHUB_TOKEN"]

# Obtener último debate de Redis
r = httpx.get(f"{redis_url}/get/memory:last_debate", headers={"Authorization": f"Bearer {redis_token}"})
debate = json.loads(r.json().get("result", "{}"))

if debate:
    debate_id = f"NEXUS-DEB-{debate.get('fecha', '').replace('T','-')[:16]}"
    content = f"# Acta del Debate\n\n**ID:** {debate_id}\n**Fecha:** {debate.get('fecha','')}\n**Tema:** {debate.get('tema','')}\n\n{debate.get('respuesta','')}"
    
    content_b64 = base64.b64encode(content.encode()).decode()
    url = f"https://api.github.com/repos/jeengrasi/Maestro_trading/contents/docs/actas/{debate_id}.md"
    
    httpx.put(url,
        headers={"Authorization": f"Bearer {github_token}", "Content-Type": "application/json"},
        json={"message": f"Acta {debate_id}", "content": content_b64, "branch": "main"}
    )
    print(f"✅ Acta {debate_id} guardada.")
else:
    print("❌ No hay debates pendientes.")
