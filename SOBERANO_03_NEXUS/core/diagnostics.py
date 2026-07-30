# ==============================================================================
# ARCHIVO: diagnostics.py
# DEPARTAMENTO: 03 - NEXUS (Núcleo)
# SISTEMA: MAESTRO-NEXUS
# ROL: Diagnóstico de Salud
# MISIÓN: Proveer endpoints y funciones para verificar el estado del sistema.
# DEBERES: Cumplir con la Constitución, no hardcodear credenciales, registrar errores.
# PROHIBICIONES: Violar las reglas transversales del Manifiesto de Roles.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

# ==============================================================================
# ARCHIVO: diagnostics.py
# MODULO: core
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Endpoint de diagnóstico seguro de APIs y conectividad (Solo Lectura).
# ULTIMA MODIFICACION: 2026-07-28
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# ==============================================================================
# [MOD-2026-07-28] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Extraer lógica de diagnóstico de index.py para reducir acoplamiento (Fase 9.1).
# REF: Principio de Separación de Responsabilidades.

import os
import httpx
import asyncio
from datetime import datetime
from fastapi import APIRouter
from SOBERANO_03_NEXUS.config import Config

router = APIRouter()

@router.get("/diagnostico")
async def diagnosticar_apis():
    """
    Prueba la conectividad de todas las APIs configuradas en Vercel.
    TODAS las claves se enmascaran automáticamente para seguridad.
    """
    resultados = {"timestamp": datetime.now().isoformat(), "apis": {}}
    
    def mask_key(key):
        if not key or len(key) < 8: return "NO_CONFIGURADA"
        return f"{key[:4]}****{key[-4:]}"
    
    async def test_llm(name, url, api_key, model, payload_override=None):
        if not api_key:
            resultados["apis"][name] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}
            return
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = payload_override or {"model": model, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 1}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.post(url, headers=headers, json=payload)
                if r.status_code == 200:
                    resultados["apis"][name] = {"estado": "✅ OK", "clave": mask_key(api_key), "http": 200}
                else:
                    resultados["apis"][name] = {"estado": f"❌ FALLÓ ({r.status_code})", "clave": mask_key(api_key), "detalle": r.text[:60]}
        except Exception as e:
            resultados["apis"][name] = {"estado": "❌ ERROR DE RED", "clave": mask_key(api_key), "detalle": str(e)[:50]}

    # 1. IAs de Lenguaje (LLMs)
    await test_llm("Mistral", "https://api.mistral.ai/v1/chat/completions", os.getenv("MISTRAL_API_KEY"), "mistral-tiny")
    await test_llm("DeepSeek", "https://api.deepseek.com/v1/chat/completions", os.getenv("DEEPSEEK_API_KEY"), "deepseek-chat")
    await test_llm("Groq", "https://api.groq.com/openai/v1/chat/completions", os.getenv("GROQ_API_KEY"), "llama3-8b-8192")
    await test_llm("OpenRouter", "https://openrouter.ai/api/v1/chat/completions", os.getenv("OPENROUTER_API_KEY"), "openrouter/auto", {"model": "openrouter/auto", "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 1})
    await test_llm("Cerebras", "https://api.cerebras.ai/v1/chat/completions", os.getenv("CEREBRAS_API_KEY"), "llama3.1-8b")
    
    nim_key = os.getenv("NVIDIA_NIM_API_KEY") or os.getenv("NVIDIA_API_KEY")
    await test_llm("NVIDIA NIM", "https://integrate.api.nvidia.com/v1/chat/completions", nim_key, "meta/llama-3.1-8b-instruct")

    gemini_key = os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                r = await client.post(url, json={"contents": [{"parts": [{"text": "Hi"}]}]})
                resultados["apis"]["Google Gemini"] = {"estado": "✅ OK" if r.status_code == 200 else f"❌ FALLÓ ({r.status_code})", "clave": mask_key(gemini_key)}
        except Exception as e:
            resultados["apis"]["Google Gemini"] = {"estado": "❌ ERROR", "clave": mask_key(gemini_key), "detalle": str(e)[:50]}
    else:
        resultados["apis"]["Google Gemini"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    cf_token = os.getenv("CLOUDFLARE_API_TOKEN")
    cf_account = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    if cf_token and cf_account:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                url = f"https://api.cloudflare.com/client/v4/accounts/{cf_account}/ai/run/@cf/meta/llama-3.1-8b-instruct"
                r = await client.post(url, headers={"Authorization": f"Bearer {cf_token}"}, json={"messages": [{"role": "user", "content": "Hi"}]})
                resultados["apis"]["Cloudflare AI"] = {"estado": "✅ OK" if r.status_code == 200 else f"❌ FALLÓ ({r.status_code})", "clave": mask_key(cf_token)}
        except Exception as e:
            resultados["apis"]["Cloudflare AI"] = {"estado": "❌ ERROR", "clave": mask_key(cf_token), "detalle": str(e)[:50]}
    else:
        resultados["apis"]["Cloudflare AI"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    hf_key = os.getenv("HUGGINGFACE_API_KEY")
    if hf_key:
        resultados["apis"]["HuggingFace"] = {"estado": "⚠️ CLAVE PRESENTE", "clave": mask_key(hf_key), "nota": "Requiere modelo específico"}
    else:
        resultados["apis"]["HuggingFace"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    # 2. Servicios de Infraestructura y Trading
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if tg_token:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"https://api.telegram.org/bot{tg_token}/getMe")
                resultados["apis"]["Telegram"] = {"estado": "✅ OK" if r.json().get("ok") else "❌ FALLÓ", "clave": mask_key(tg_token)}
        except:
            resultados["apis"]["Telegram"] = {"estado": "❌ ERROR", "clave": mask_key(tg_token)}
    else:
        resultados["apis"]["Telegram"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    alpaca_key = os.getenv("ALPACA_API_KEY")
    alpaca_secret = os.getenv("ALPACA_SECRET_KEY")
    if alpaca_key and alpaca_secret:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                headers = {"APCA-API-KEY-ID": alpaca_key, "APCA-API-SECRET-KEY": alpaca_secret}
                is_paper = os.getenv("ALPACA_PAPER", "true").strip().lower() == "true"
                url = "https://paper-api.alpaca.markets/v2/account" if is_paper else "https://api.alpaca.markets/v2/account"
                r = await client.get(url, headers=headers)
                resultados["apis"]["Alpaca"] = {"estado": "✅ OK" if r.status_code == 200 else f"❌ FALLÓ ({r.status_code})", "clave": mask_key(alpaca_key), "modo": "Paper" if is_paper else "Real"}
        except Exception as e:
            resultados["apis"]["Alpaca"] = {"estado": "❌ ERROR", "clave": mask_key(alpaca_key), "detalle": str(e)[:50]}
    else:
        resultados["apis"]["Alpaca"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
    redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    if redis_url and redis_token:
        try:
            from upstash_redis import Redis
            r_client = Redis(url=redis_url, token=redis_token)
            r = await asyncio.wait_for(asyncio.to_thread(r_client.ping), timeout=2.0)
            resultados["apis"]["Upstash Redis"] = {"estado": "✅ OK" if (r == "PONG" or r is True) else "❌ FALLÓ", "clave": mask_key(redis_token)}
        except:
            resultados["apis"]["Upstash Redis"] = {"estado": "❌ ERROR", "clave": mask_key(redis_token)}
    else:
        resultados["apis"]["Upstash Redis"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    gh_token = os.getenv("GITHUB_TOKEN")
    if gh_token:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get("https://api.github.com/user", headers={"Authorization": f"Bearer {gh_token}", "User-Agent": "Nexus-Diagnostic"})
                resultados["apis"]["GitHub"] = {"estado": "✅ OK" if r.status_code == 200 else f"❌ FALLÓ ({r.status_code})", "clave": mask_key(gh_token)}
        except:
            resultados["apis"]["GitHub"] = {"estado": "❌ ERROR", "clave": mask_key(gh_token)}
    else:
        resultados["apis"]["GitHub"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    railway_token = os.getenv("RAILWAY_TOKEN") or os.getenv("RAILWAY_API_TOKEN")
    if railway_token:
        resultados["apis"]["Railway"] = {"estado": "⚠️ CLAVE PRESENTE", "clave": mask_key(railway_token)}
    else:
        resultados["apis"]["Railway"] = {"estado": "FALTANTE", "clave": "NO_CONFIGURADA"}

    return resultados
