# ==============================================================================
# ARCHIVO: core.py
# MODULO: parliament
# DEPARTAMENTO: 03 - NEXUS (Parlamento)
# SISTEMA: MAESTRO-NEXUS
# ROL: El Cerebro Cognitivo
# MISIÓN: Orquestar el Tool-Calling, aplicar reglas EDVC y mantener la ventana de contexto conversacional.
# DEBERES: Gestionar memoria deslizante, aplicar concisión (250 palabras), invocar herramientas (max 2/turno).
# PROHIBICIONES: Ejecutar órdenes de trading directamente, almacenar datos permanentemente en disco.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

import json
import httpx
from SOBERANO_03_NEXUS.parliament.tool_caller import MISTRAL_TOOLS, execute_tool
from SOBERANO_03_NEXUS.parliament.github_rag import obtener_contexto_gobierno
import os
import logging
from datetime import datetime
from SOBERANO_03_NEXUS.providers.mistral import call_mistral

logger = logging.getLogger(__name__)

PARLIAMENT_STACK = {
    "gerente": "Mistral (Decisión final, estrategia)",
    "analista": "Mistral (Análisis técnico)",
    "auditor": "Mistral (Validación de riesgos)",
    "estratega": "Mistral (Análisis financiero)",
    "secretario": "Mistral (Generación de actas)"
}

def leer_contexto_obligatorio(redis_client=None) -> str:
    # [MOD-2026-07-27] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
    # MOTIVO: Migrar lectura de contexto a Redis para persistencia en Vercel, con fallback a local.
    # REF: Limitación de filesystem efímero en Vercel Serverless.
    if redis_client:
        try:
            registros = redis_client.lrange("memoria:bitacora:general", 0, 29)
            if registros:
                return "\n".join([r.decode('utf-8') for r in reversed(registros)])
        except Exception as e:
            logger.error(f"Error leyendo bitácora de Redis: {e}")
    
    # Fallback a archivo local (para ejecución local en Termux)
    bitacora_path = "SOBERANO_01_MEMORIA/bitacora.md"
    try:
        if not os.path.exists(bitacora_path):
            return "No hay historial previo disponible."
        with open(bitacora_path, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            return "".join(lineas[-30:]) if len(lineas) > 30 else "".join(lineas)
    except Exception as e:
        logger.error(f"Error leyendo bitácora local: {e}")
        return "Error al leer historial."

def escribir_en_bitacora(redis_client, accion: str, resultado: str):
    # [MOD-2026-07-27] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
    # MOTIVO: Migrar escritura de bitácora a Redis para persistencia en Vercel.
    # REF: Limitación de filesystem efímero en Vercel Serverless.
    if redis_client:
        try:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            registro = f"[{fecha}] {accion}: {resultado[:200]}"
            redis_client.lpush("memoria:bitacora:general", registro)
            redis_client.ltrim("memoria:bitacora:general", 0, 99)
            redis_client.expire("memoria:bitacora:general", 86400 * 30)
        except Exception as e:
            logger.error(f"Error escribiendo en Redis: {e}")
    else:
        # Fallback a archivo local
        bitacora_path = "SOBERANO_01_MEMORIA/bitacora.md"
        try:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            nuevo_registro = f"\n- **{fecha}** | **{accion}** | {resultado[:150]}...\n"
            with open(bitacora_path, "a", encoding="utf-8") as f:
                f.write(nuevo_registro)
        except Exception as e:
            logger.error(f"Error escribiendo en bitácora local: {e}")

def sanitize_prompt(prompt: str) -> str:
    return prompt.strip()

async def call_ia(role: str, message: str, redis_client=None, chat_id: str = None) -> str:
    contexto = leer_contexto_obligatorio(redis_client)
    
    # [MOD-2026-07-27] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
    # MOTIVO: Integrar Norma EDVC v1.0 en el system prompt para garantizar trazabilidad.
    # REF: SOBERANO_00_GOBIERNO/NORMAS.md
    edvc_instruction = """

🚨 INSTRUCCION CRITICA (NORMA EDVC v1.0):
Si en tu respuesta debes generar o modificar codigo, DEBES aplicar estrictamente las 4 capas del estandar EDVC:
1. CAPA 1: Cedula de Identidad (Encabezado con ARCHIVO, SISTEMA, PROPOSITO, FECHA, AUTOR, VALIDADOR, AUDITORIA).
2. CAPA 2: Contexto de Seccion (Explicar el PORQUE arquitectonico antes de bloques logicos).
3. CAPA 3: La Cicatriz Quirurgica (Etiqueta [MOD-YYYY-MM-DD] [AUTOR] [VALIDADOR] MOTIVO: REF: antes de cambios criticos).
4. CAPA 4: Changelog Vivo (Registro cronologico inverso al final del archivo).
PROHIBIDO: Comentar cada linea individual o dejar codigo comentado sin etiqueta [DEPRECATED].
Si no cumples, tu respuesta sera rechazada por el Auditor de Riesgos.

🚨 REGLA DE EXPLICABILIDAD (XAI): Si el usuario pregunta 'por qué', 'razón' o 'motivo' de una decisión, TIENES PROHIBIDO inventar una respuesta. DEBES usar obligatoriamente tus herramientas (github_rag o lectura de archivos) para consultar SOBERANO_01_MEMORIA/bitacora.md o las normas antes de responder.

🚨 REGLA DE HERRAMIENTAS: Si una herramienta devuelve un mensaje que comienza con '[ERROR DE HERRAMIENTA]', tienes PROHIBIDO volver a llamarla. Debes informar inmediatamente al Director con el mensaje de error exacto.
"""
    
    # [MOD-2026-07-28] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
    # MOTIVO: Protocolo de Concision Ejecutiva. Respuestas de max 250 palabras,
    #         conclusion al inicio, uso de vinetas, cero relleno.
    # REF: Solicitud del Director para respuestas mas concretas y entendibles.
    concision_rule = """

REGLAS DE CONCISION EJECUTIVA (OBLIGATORIO):
1. MAXIMO 250 palabras en total.
2. La CONCLUSION o VEREDICTO va PRIMERO, en la primera linea.
3. Usa vinetas (-) para listar datos, riesgos o argumentos.
4. CERO relleno, CERO frases de cortesia, CERO introducciones largas.
5. Si te preguntan por un activo, da: precio, tendencia, riesgo, veredicto. Nada mas.
6. Formato: Markdown simple, sin tablas complejas que se rompan en Telegram.
"""
    
    # [MOD-2026-07-29] Inyección de contexto de gobierno si la pregunta es normativa
    contexto_normativo = ""
    if any(palabra in message.lower() for palabra in ["norma", "regla", "constitucion", "riesgo", "art.", "gobierno"]):
        try:
            contexto_normativo = await obtener_contexto_gobierno()
        except Exception as e:
            logger.error(f"Error obteniendo contexto GitHub: {e}")
    
    contexto_final = f"{contexto}\n\n{contexto_normativo}" if contexto_normativo else contexto

    system_prompts = {
        "gerente": f"Eres el Gerente General del Parlamento Nexus. Das veredictos ejecutivos finales.\nContexto:\n{contexto_final}\n{concision_rule}",
        "analista": f"Eres el Analista Tecnico. Das datos duros y tendencias en formato ejecutivo.\nContexto:\n{contexto_final}\n{concision_rule}",
        "auditor": f"Eres el Auditor de Riesgos (Art. 14: max 1% riesgo, VIX max 20). Vetar si se excede.\nContexto:\n{contexto_final}\n{concision_rule}",
        "estratega": f"Eres el Estratega de Mercado. Das recomendaciones de inversion con datos.\nContexto:\n{contexto_final}\n{concision_rule}",
        "secretario": f"Eres el Secretario. Generas actas ultra-brevias y claras.\nContexto:\n{contexto_final}\n{concision_rule}"
    }
    
    system_prompt = system_prompts.get(role, system_prompts["gerente"]) + edvc_instruction + history_context
    
    logger.info(f"🧠 Llamando a Mistral para rol: {role} (Con Tool-Calling)")
    
    # FASE 12.1: Bucle de Tool-Calling (Máximo 2 iteraciones para evitar bucles infinitos)
    max_tool_calls = 2
    # --- INICIO: MEMORIA DESLIZANTE (CRECIMIENTO COGNITIVO) ---
    history_context = ""
    if chat_id and redis_client:
        history_key = f"chat_history:{chat_id}"
        history = redis_client.lrange(history_key, 0, 3) # Últimos 4 mensajes
        history.reverse()
        if history:
            history_context = "\n[CONTEXTO DE CONVERSACIÓN RECIENTE]\n"
            for h in history:
                h_str = h.decode() if isinstance(h, bytes) else h
                history_context += f"{h_str}\n"
            history_context += "[FIN CONTEXTO]\n"
        # Guardar el nuevo mensaje del usuario
        redis_client.lpush(history_key, f"Usuario: {message}")
        redis_client.expire(history_key, 3600) # TTL 1 hora
    # --- FIN: MEMORIA DESLIZANTE ---

    messages_history = [
        {"role": "system", "content": system_prompts.get(role, system_prompts["gerente"]) + edvc_instruction + history_context + history_context},
        {"role": "user", "content": message}
    ]
    
    respuesta = ""
    for _ in range(max_tool_calls):
        api_key = os.getenv("MISTRAL_API_KEY")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "mistral-small-latest",
            "messages": messages_history,
            "tools": MISTRAL_TOOLS,
            "tool_choice": "auto"
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload)
            
        if r.status_code == 200:
            msg = r.json()["choices"][0]["message"]
            if "tool_calls" in msg and msg["tool_calls"]:
                tool_call = msg["tool_calls"][0]
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])
                
                logger.info(f"🛠️ Ejecutando herramienta: {func_name}")
                tool_result = await execute_tool(func_name, func_args, redis_client)
                
                messages_history.append(msg)
                messages_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": tool_result
                })
            else:
                respuesta = msg.get("content", "Sin respuesta de la IA.")
                break
        else:
            respuesta = f"Error en Mistral: {r.status_code} - {r.text[:100]}"
            break
            
    if not respuesta:
        respuesta = "Límite de herramientas alcanzado."

    escribir_en_bitacora(redis_client, f"CONSULTA_{role.upper()}", f"P: {message[:50]} | R: {respuesta[:50]}")
    

    # --- FASE 2: GUARDAR RESPUESTA EN MEMORIA DESLIZANTE ---
    if chat_id and redis_client:
        try:
            history_key = f"chat_history:{chat_id}"
            redis_client.lpush(history_key, f"Asistente: {respuesta[:300]}...")
            redis_client.expire(history_key, 3600)
        except Exception as e:
            logger.error(f"Error guardando respuesta en memoria: {e}")
    # --- FIN GUARDAR RESPUESTA ---
    return respuesta
