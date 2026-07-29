# ==============================================================================
# ARCHIVO: tool_caller.py
# MODULO: parliament
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Motor de Tool-Calling nativo para Mistral. Permite a la IA ejecutar
#            acciones reales sobre las Apps Nucleares (GitHub, Alpaca, Redis).
# ULTIMA MODIFICACION: 2026-07-29
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# ==============================================================================
# [MOD-2026-07-29] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Fase 12.1 - Evolucionar el bot de "solo texto" a "agente que actúa".
# REF: Documentación oficial Mistral Function Calling + LangGraph ReAct Pattern.

import os
import httpx
import logging

logger = logging.getLogger(__name__)

# Definición de herramientas para Mistral (Formato oficial)
MISTRAL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_alpaca_data",
            "description": "Obtiene datos de mercado (precio, VIX, volumen) de un ticker desde Alpaca Markets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "El símbolo del activo, ej: 'AAPL', 'SPY'."}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_github_file",
            "description": "Lee el contenido de un archivo de gobierno o configuración desde GitHub API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Ruta del archivo, ej: 'SOBERANO_00_GOBIERNO/NORMAS.md'."}
                },
                "required": ["filepath"]
            }
        }
    }
]

async def execute_tool(tool_name: str, arguments: dict, redis_client=None) -> str:
    """Ejecuta la herramienta solicitada y devuelve el resultado como string para la IA."""
    try:
        if tool_name == "get_alpaca_data":
            ticker = arguments.get("ticker", "").upper()
            api_key = os.getenv("ALPACA_API_KEY")
            api_secret = os.getenv("ALPACA_SECRET_KEY")
            is_paper = os.getenv("ALPACA_PAPER", "true").lower() == "true"
            base_url = "https://paper-api.alpaca.markets" if is_paper else "https://api.alpaca.markets"
            
            headers = {"APCA-API-KEY-ID": api_key, "APCA-API-SECRET-KEY": api_secret}
            
            # Intento 1: Barra de 1 día
            url_day = f"{base_url}/v2/stocks/{ticker}/bars?timeframe=1Day&limit=1"
            async with httpx.AsyncClient(timeout=10.0) as client:
                r_day = await client.get(url_day, headers=headers)
            
            if r_day.status_code == 200:
                bars = r_day.json().get("bars", [])
                if bars:
                    bar = bars[0]
                    return f"Datos de {ticker} (Diario): Precio=${bar.get('c')}, Volumen={bar.get('v')}. (Modo: {'Paper' if is_paper else 'Real'})"
            
            # Intento 2 (Fallback): Si no hay barra diaria (ej. mercado cerrado), buscar la última de 1 minuto
            url_min = f"{base_url}/v2/stocks/{ticker}/bars?timeframe=1Min&limit=1&sort=desc"
            async with httpx.AsyncClient(timeout=10.0) as client:
                r_min = await client.get(url_min, headers=headers)
            
            if r_min.status_code == 200:
                bars_min = r_min.json().get("bars", [])
                if bars_min:
                    bar_min = bars_min[0]
                    return f"Datos de {ticker} (Última cotización): Precio=${bar_min.get('c')}. (Mercado cerrado o sin datos diarios. Modo: {'Paper' if is_paper else 'Real'})"
            
            # Fallo total
            return f"ADVERTENCIA CRÍTICA: No se encontraron datos de mercado para {ticker} en Alpaca (ni diarios ni recientes). No inventes precios. Informa al Director que el activo no tiene datos disponibles."


        elif tool_name == "get_github_file":
            filepath = arguments.get("filepath", "")
            gh_token = os.getenv("GITHUB_TOKEN")
            repo = "jeengrasi/Maestro_trading"
            branch = "soberano-v1"
            
            headers = {
                "Authorization": f"Bearer {gh_token}",
                "Accept": "application/vnd.github.v3.raw",
                "User-Agent": "Nexus-ToolCaller"
            }
            url = f"https://api.github.com/repos/{repo}/contents/{filepath}?ref={branch}"
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(url, headers=headers)
            if r.status_code == 200:
                # Limitamos a 1500 caracteres para no saturar el contexto de Mistral
                return f"Contenido de {filepath}:\n{r.text[:1500]}..."
            return f"Error leyendo GitHub: HTTP {r.status_code} - {r.text[:100]}"
        
        else:
            return f"Error: Herramienta '{tool_name}' no reconocida."
            
    except Exception as e:
        logger.error(f"Error ejecutando herramienta {tool_name}: {e}")
        return f"Error interno ejecutando {tool_name}: {str(e)[:100]}"
