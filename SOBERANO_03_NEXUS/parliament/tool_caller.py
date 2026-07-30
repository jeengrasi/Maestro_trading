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
            """
            Obtiene datos de mercado de Alpaca usando la API oficial de Market Data.
            Documentación: https://docs.alpaca.markets/docs/market-data
            """
            ticker = arguments.get("ticker", "").upper()
            
            # Credenciales (siempre usar .strip() para evitar espacios)
            api_key = os.getenv("ALPACA_API_KEY", "").strip()
            api_secret = os.getenv("ALPACA_SECRET_KEY", "").strip()
            
            if not api_key or not api_secret:
                return "[ERROR DE HERRAMIENTA]: Credenciales de Alpaca no configuradas. Verifique ALPACA_API_KEY y ALPACA_SECRET_KEY en Vercel."
            
            # Endpoint oficial de Market Data (NO distingue entre paper/real)
            data_url = "https://data.alpaca.markets"
            headers = {
                "APCA-API-KEY-ID": api_key,
                "APCA-API-SECRET-KEY": api_secret
            }
            
            try:
                # Obtener última barra diaria
                url = f"{data_url}/v2/stocks/{ticker}/bars?timeframe=1Day&limit=1"
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    bars = data.get("bars", [])
                    if bars and len(bars) > 0:
                        bar = bars[0]
                        precio = bar.get("c")
                        volumen = bar.get("v")
                        fecha = bar.get("t", "Fecha no disponible")
                        
                        # Calcular tendencia simple
                        tendencia = "NEUTRAL"
                        if len(bars) > 1:
                            precio_anterior = bars[1].get("c")
                            if precio > precio_anterior:
                                tendencia = "ALCISTA"
                            elif precio < precio_anterior:
                                tendencia = "BAJISTA"
                        
                        return f"✅ Datos de {ticker} (Alpaca Market Data):\n- Precio: ${precio}\n- Volumen: {volumen}\n- Tendencia: {tendencia}\n- Fecha: {fecha}"
                    else:
                        return f"[ERROR DE HERRAMIENTA]: No se encontraron barras de precio para {ticker}."
                else:
                    return f"[ERROR DE HERRAMIENTA]: Alpaca respondió con código {response.status_code}. Detalle: {response.text[:100]}"
                    
            except Exception as e:
                return f"[ERROR DE HERRAMIENTA]: Excepción al consultar Alpaca: {str(e)[:100]}"

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
