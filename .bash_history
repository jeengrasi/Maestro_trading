    
puntos_router = [
    "return respuesta",
    "return response",
    "async def procesar_intencion",
    "def procesar_intencion"
]
for p in puntos_router:
    if p in router:
        print(f"   ✅ Encontrado: '{p}'")
    else:
        print(f"   ❌ NO encontrado: '{p}'")

# 3. Mostrar líneas clave de router.py para ver su estructura real
print("\n📍 Últimas 20 líneas de router.py (para ver el return final):")
lines = router.split('\n')
for i, line in enumerate(lines[-20:]):
    print(f"{len(lines)-19+i:4d}: {line}")

print("\n" + "=" * 80)
print("✅ DIAGNÓSTICO COMPLETO. Con esto, haré modificaciones seguras.")
EOF

python3 << 'EOF'
import re

core_path = "SOBERANO_03_NEXUS/parliament/core.py"
print(f"🔍 EXTRAYENDO FUNCIÓN call_ia DE {core_path}...")
print("=" * 80)

with open(core_path, "r", encoding="utf-8") as f:
    content = f.read()

# Buscar la función async def call_ia y extraer su contenido hasta la siguiente función o el final del archivo
pattern = r'(async def call_ia\(.*?\):)(.*?)(?=\nasync def |\ndef |\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    func_code = match.group(0)
    lines = func_code.split('\n')
    print(f"📄 FUNCIÓN call_ia ENCONTRADA ({len(lines)} líneas):")
    print("-" * 80)
    for i, line in enumerate(lines):
        # Mostrar solo las primeras 60 líneas para no saturar, que es donde suele estar la lógica de mensajes
        if i < 60:
            print(f"{i+1:4d}: {line}")
        elif i == 60:
            print("     ... (resto de la función omitido para brevedad) ...")
    print("-" * 80)
else:
    print("⚠️ No se encontró la función 'async def call_ia'.")
    print("Mostrando las primeras 80 líneas del archivo para contexto:")
    print("-" * 80)
    for i, line in enumerate(content.split('\n')[:80]):
        print(f"{i+1:4d}: {line}")
    print("-" * 80)

print("\n✅ EXTRACCIÓN COMPLETADA.")
print("👉 Copie y pegue esta salida. Con esto, sabré exactamente dónde y cómo inyectar la memoria deslizante sin romper nada.")
print("=" * 80)
EOF

python3 << 'EOF'
import os

print("🔍 INICIANDO MODIFICACIÓN QUIRÚRGICA SEGURA (DÍA 1: CRECIMIENTO COGNITIVO)...")

# ==========================================
# PASO 1: MODIFICAR parliament/core.py
# ==========================================
core_path = "SOBERANO_03_NEXUS/parliament/core.py"
with open(core_path, "r", encoding="utf-8") as f:
    core_content = f.read()

# 1.1 Actualizar firma de la función
old_sig = "async def call_ia(role: str, message: str, redis_client=None) -> str:"
new_sig = "async def call_ia(role: str, message: str, redis_client=None, chat_id: str = None) -> str:"
if old_sig in core_content:
    core_content = core_content.replace(old_sig, new_sig)
    print("✅ core.py: Firma de call_ia actualizada para recibir chat_id.")
else:
    print("⚠️ core.py: No se encontró la firma exacta.")

# 1.2 Inyectar memoria deslizante antes de messages_history
old_messages = """    messages_history = [
        {"role": "system", "content": system_prompts.get(role, system_prompts["gerente"]) + edvc_instruction},
        {"role": "user", "content": message}
    ]"""

new_messages = """    # --- INICIO: MEMORIA DESLIZANTE (CRECIMIENTO COGNITIVO) ---
    history_context = ""
    if chat_id and redis_client:
        history_key = f"chat_history:{chat_id}"
        history = redis_client.lrange(history_key, 0, 3) # Últimos 4 mensajes
        history.reverse()
        if history:
            history_context = "\\n[CONTEXTO DE CONVERSACIÓN RECIENTE]\\n"
            for h in history:
                h_str = h.decode() if isinstance(h, bytes) else h
                history_context += f"{h_str}\\n"
            history_context += "[FIN CONTEXTO]\\n"
        # Guardar el nuevo mensaje del usuario
        redis_client.lpush(history_key, f"Usuario: {message}")
        redis_client.expire(history_key, 3600) # TTL 1 hora
    # --- FIN: MEMORIA DESLIZANTE ---

    messages_history = [
        {"role": "system", "content": system_prompts.get(role, system_prompts["gerente"]) + edvc_instruction + history_context},
        {"role": "user", "content": message}
    ]"""

if old_messages in core_content:
    core_content = core_content.replace(old_messages, new_messages)
    print("✅ core.py: Lógica de memoria deslizante inyectada con éxito.")
else:
    print("⚠️ core.py: No se encontró el bloque messages_history exacto.")

with open(core_path, "w", encoding="utf-8") as f:
    f.write(core_content)

# ==========================================
# PASO 2: CREAR core/memory_logger.py
# ==========================================
logger_path = "SOBERANO_03_NEXUS/core/memory_logger.py"
logger_content = """# ==============================================================================
# ARCHIVO: memory_logger.py
# MODULO: core
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Registrar decisiones y uso de herramientas en la Bitácora Soberana.
#            Cumple el Art. 5: "La memoria es el sistema, no la memoria de la IA".
# ==============================================================================
import os
import datetime

def registrar_en_bitacora(chat_id: str, accion: str, herramientas_usadas: list, resultado_resumen: str):
    \"\"\"
    Escribe una entrada estructurada en la bitácora del sistema.
    \"\"\"
    bitacora_path = "SOBERANO_01_MEMORIA/bitacora.md"
    
    os.makedirs("SOBERANO_01_MEMORIA", exist_ok=True)
    
    if not os.path.exists(bitacora_path):
        with open(bitacora_path, "w", encoding="utf-8") as f:
            f.write("# 📝 BITÁCORA SOBERANA DEL SISTEMA MAESTRO-NEXUS\\n\\n")
            f.write("*La memoria es el sistema, no la memoria de la IA. (Art. 5)*\\n\\n---\\n\\n")
    
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    herramientas_str = ", ".join(herramientas_usadas) if herramientas_usadas else "Ninguna"
    
    entrada = f\"\"\"
---
id: LOG-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}
fecha: {fecha}
chat_id: {chat_id}
accion: {accion}
herramientas: [{herramientas_str}]
---
**[RESUMEN DE LA INTERACCIÓN]**
{resultado_resumen}

---
\"\"\"
    
    with open(bitacora_path, "a", encoding="utf-8") as f:
        f.write(entrada)
"""
with open(logger_path, "w", encoding="utf-8") as f:
    f.write(logger_content)
print("✅ Creado: core/memory_logger.py")

# ==========================================
# PASO 3: MODIFICAR core/router.py
# ==========================================
router_path = "SOBERANO_03_NEXUS/core/router.py"
with open(router_path, "r", encoding="utf-8") as f:
    router_content = f.read()

# 3.1 Agregar importación
if "from SOBERANO_03_NEXUS.core.memory_logger import registrar_en_bitacora" not in router_content:
    lines = router_content.split('\n')
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_idx = i + 1
    lines.insert(insert_idx, "from SOBERANO_03_NEXUS.core.memory_logger import registrar_en_bitacora")
    router_content = '\n'.join(lines)
    print("✅ router.py: Importación de memory_logger agregada.")

# 3.2 Inyectar llamada al logger y pasar chat_id a call_ia
old_router_call = """        respuesta = await call_ia(rol, text, redis_client=redis_client)
        await send_telegram_func(respuesta, chat_id=chat_id)"""

new_router_call = """        respuesta = await call_ia(rol, text, redis_client=redis_client, chat_id=chat_id)
        
        # Registro soberano en bitácora (Art. 5)
        registrar_en_bitacora(
            chat_id=str(chat_id),
            accion=f"Consulta rol: {rol}",
            herramientas_usadas=["call_ia"],
            resultado_resumen=f"P: {text[:80]}... | R: {respuesta[:80]}..."
        )
        
        await send_telegram_func(respuesta, chat_id=chat_id)"""

if old_router_call in router_content:
    router_content = router_content.replace(old_router_call, new_router_call)
    print("✅ router.py: Llamada a call_ia actualizada y logger inyectado.")
else:
    print("⚠️ router.py: No se encontró el bloque de llamada exacto.")

with open(router_path, "w", encoding="utf-8") as f:
    f.write(router_content)

print("\n📝 Preparando validación de sintaxis...")
EOF

# ==========================================
# PASO 4: VALIDACIÓN DE SINTAXIS
# ==========================================
echo ""
echo "🔍 VALIDANDO SINTAXIS DEL SISTEMA..."
python3 -m py_compile SOBERANO_03_NEXUS/parliament/core.py && echo "✅ core.py: SINTAXIS CORRECTA" || echo "❌ core.py: ERROR"
python3 -m py_compile SOBERANO_03_NEXUS/core/memory_logger.py && echo "✅ memory_logger.py: SINTAXIS CORRECTA" || echo "❌ memory_logger.py: ERROR"
python3 -m py_compile SOBERANO_03_NEXUS/core/router.py && echo "✅ router.py: SINTAXIS CORRECTA" || echo "❌ router.py: ERROR"
echo ""
echo "=================================================="
echo "🌱 CRECIMIENTO COGNITIVO (DÍA 1) IMPLEMENTADO."
echo "El sistema ahora recuerda el contexto inmediato y"
echo "escribe sus decisiones en la Bitácora Soberana."
echo ""
echo "Si la sintaxis es CORRECTA, ejecute:"
echo ""
echo "git add SOBERANO_03_NEXUS/parliament/core.py SOBERANO_03_NEXUS/core/memory_logger.py SOBERANO_03_NEXUS/core/router.py"
echo "git commit -m '[CRECIMIENTO DÍA 1] Memoria deslizante en Redis y registro soberano en bitácora.md (Art. 5)'"
echo "git push origin soberano-v1"
echo "=================================================="
git add SOBERANO_03_NEXUS/parliament/core.py SOBERANO_03_NEXUS/core/memory_logger.py SOBERANO_03_NEXUS/core/router.py
git commit -m '[CRECIMIENTO DÍA 1] Memoria deslizante en Redis y registro soberano en bitácora.md (Art. 5)'
git push origin soberano-v1
python3 << 'EOF'
import os
import re
import json
import hashlib
import py_compile
import subprocess
from pathlib import Path

print("🛡️ AUDITORÍA INSTITUCIONAL v2.0 + CHECK DE FIRMAS...")
print("=" * 90)

reporte = []
errores_criticos = 0

# 1. SINTAXIS
print("\n📝 1. SINTAXIS PYTHON...")
archivos_py = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', '.venv', 'node_modules', '.local', '.cache', '.railway']]
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            archivos_py.append(filepath)
            try:
                py_compile.compile(filepath, doraise=True)
            except py_compile.PyCompileError as e:
                print(f"   ❌ {filepath}")
                errores_criticos += 1
print(f"   ✅ {len(archivos_py)} archivos validados." if errores_criticos == 0 else f"   ❌ {errores_criticos} errores.")

# 2. RAÍZ
print("\n📂 2. RAÍZ (Art. 9)...")
archivos_raiz = [f for f in os.listdir('.') if os.path.isfile(f)]
permitidos = {'.env', '.gitignore', 'vercel.json', 'requirements.txt', 'README.md', '.bash_history', 'termux.properties'}
sospechosos = [f for f in archivos_raiz if f not in permitidos and not f.startswith('.')]
if not sospechosos:
    print("   ✅ Raíz limpia.")
else:
    print(f"   ⚠️ Archivos no estándar: {sospechosos}")

# 3. INTEGRIDAD
print("\n🔐 3. INTEGRIDAD DE GOBIERNO...")
for archivo in ["SOBERANO_00_GOBIERNO/CONSTITUCION.md", "SOBERANO_00_GOBIERNO/NORMAS.md", "SOBERANO_03_NEXUS/config.py"]:
    if os.path.exists(archivo):
        with open(archivo, "rb") as f:
            print(f"   ✅ {archivo}: {hashlib.sha256(f.read()).hexdigest()[:16]}...")
    else:
        print(f"   ❌ {archivo}: NO ENCONTRADO")
        errores_criticos += 1

# 4. DEPENDENCIAS
print("\n📦 4. DEPENDENCIAS...")
if os.path.exists("requirements.txt"):
    with open("requirements.txt") as f:
        reqs = [l.strip().split('==')[0].lower() for l in f if l.strip() and not l.startswith('#')]
    faltantes = [l for l in ["httpx", "upstash-redis", "python-dotenv", "fastapi"] if l.replace('-','_') not in reqs and l not in reqs]
    print(f"   ✅ OK" if not faltantes else f"   ❌ Faltan: {faltantes}")
else:
    print("   ❌ requirements.txt ausente")

# 5. VERCEL.JSON
print("\n⚙️ 5. VERCEL.JSON...")
if os.path.exists("vercel.json"):
    try:
        with open("vercel.json") as f: json.load(f)
        print("   ✅ JSON válido.")
    except: print("   ❌ JSON inválido.")

# 6. CREDENCIALES
print("\n🔑 6. CREDENCIALES (Art. 12)...")
patron = re.compile(r'(?:api_key|secret|token|password)\s*=\s*["\'][a-zA-Z0-9_\-]{10,}["\']', re.IGNORECASE)
secretos = []
for fp in archivos_py:
    with open(fp, "r", encoding="utf-8") as f:
        for line in f:
            if patron.search(line) and not line.strip().startswith('#'):
                secretos.append(fp)
                break
print(f"   ✅ Cero credenciales hardcodeadas." if not secretos else f"   ❌ Secretos en: {secretos}")

# 7. __init__.py
print("\n📁 7. __init__.py...")
init_faltantes = []
for root, dirs, files in os.walk('SOBERANO_03_NEXUS'):
    dirs[:] = [d for d in dirs if d not in ['__pycache__']]
    py_files = [f for f in files if f.endswith('.py') and f != '__init__.py']
    if py_files and '__init__.py' not in files:
        init_faltantes.append(root)
print(f"   ✅ Todos presentes." if not init_faltantes else f"   ⚠️ Faltan en: {init_faltantes}")

# 8. GIT
print("\n🌿 8. GIT...")
try:
    status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    print("   ✅ Working tree limpio." if not status.stdout.strip() else "   ⚠️ Cambios pendientes.")
except: print("   ⚠️ No verificado.")

# ==========================================
# 9. CHECK EXTRA: FIRMAS DE FUNCIONES (CAUSA DEL SILENCIO)
# ==========================================
print("\n🔍 9. AUDITORÍA DE FIRMAS (DIAGNÓSTICO DE SILENCIO)...")

# 9.1 procesar_intencion en router.py
with open("SOBERANO_03_NEXUS/core/router.py", "r") as f:
    router = f.read()
match = re.search(r'async def procesar_intencion\((.*?)\):', router, re.DOTALL)
if match:
    args = match.group(1).strip()
    print(f"   📄 procesar_intencion({args})")
    if "chat_id" in args:
        print("   ✅ 'chat_id' está en los argumentos.")
    else:
        print("   ❌ CRÍTICO: 'chat_id' NO está en los argumentos de procesar_intencion.")
        print("      ➡️ ESTA ES LA CAUSA PROBABLE DEL SILENCIO DEL BOT.")
        print("      ➡️ La línea 'chat_id=chat_id' lanza NameError en Vercel.")
        errores_criticos += 1

# 9.2 call_ia en core.py
with open("SOBERANO_03_NEXUS/parliament/core.py", "r") as f:
    core = f.read()
if "chat_id" in re.search(r'async def call_ia\((.*?)\):', core, re.DOTALL).group(1):
    print("   ✅ call_ia tiene 'chat_id' en sus argumentos.")
else:
    print("   ❌ call_ia no tiene 'chat_id'.")
    errores_criticos += 1

# RESUMEN
print("\n" + "=" * 90)
if errores_criticos == 0:
    print("🟢 VEREDICTO: SISTEMA 100% SANO.")
else:
    print(f"🔴 VEREDICTO: {errores_criticos} ERRORES CRÍTICOS. Ver sección 9.")
print("=" * 90)
EOF

python3 << 'EOF'
import os

print("🔧 INICIANDO CORRECCIÓN DE COMPATIBILIDAD CON VERCEL (READ-ONLY FILE SYSTEM)...")

# 1. Actualizar memory_logger.py para que sea a prueba de fallos en Vercel
logger_path = "SOBERANO_03_NEXUS/core/memory_logger.py"
safe_logger_content = """# ==============================================================================
# ARCHIVO: memory_logger.py
# MODULO: core
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Registrar decisiones en la Bitácora Soberana.
#            Compatible con Vercel (Read-Only File System) usando fallback a Redis.
# ==============================================================================
import os
import datetime
import logging

logger = logging.getLogger(__name__)

def registrar_en_bitacora(chat_id: str, accion: str, herramientas_usadas: list, resultado_resumen: str, redis_client=None):
    \"\"\"
    Escribe una entrada estructurada en la bitácora del sistema.
    Si el entorno es de solo lectura (ej. Vercel), hace fallback seguro a Redis.
    \"\"\"
    bitacora_path = "SOBERANO_01_MEMORIA/bitacora.md"
    
    try:
        os.makedirs("SOBERANO_01_MEMORIA", exist_ok=True)
        
        if not os.path.exists(bitacora_path):
            with open(bitacora_path, "w", encoding="utf-8") as f:
                f.write("# 📝 BITÁCORA SOBERANA DEL SISTEMA MAESTRO-NEXUS\\n\\n")
                f.write("*La memoria es el sistema, no la memoria de la IA. (Art. 5)*\\n\\n---\\n\\n")
        
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        herramientas_str = ", ".join(herramientas_usadas) if herramientas_usadas else "Ninguna"
        
        entrada = f\"\"\"
---
id: LOG-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}
fecha: {fecha}
chat_id: {chat_id}
accion: {accion}
herramientas: [{herramientas_str}]
---
**[RESUMEN DE LA INTERACCIÓN]**
{resultado_resumen}

---
\"\"\"
        with open(bitacora_path, "a", encoding="utf-8") as f:
            f.write(entrada)
            
    except (OSError, PermissionError) as e:
        # Fallback para entornos serverless de solo lectura (Vercel)
        logger.warning(f"Entorno de solo lectura detectado. Fallback a Redis: {e}")
        if redis_client:
            try:
                redis_key = f"bitacora_fallback:{chat_id}"
                entry = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {accion} | {resultado_resumen[:100]}"
                redis_client.lpush(redis_key, entry)
                redis_client.expire(redis_key, 86400) # 24 horas
            except Exception as redis_e:
                logger.error(f"Fallo en fallback de Redis: {redis_e}")
"""

with open(logger_path, "w", encoding="utf-8") as f:
    f.write(safe_logger_content)
print("✅ memory_logger.py: Actualizado para ser compatible con Vercel (Fallback a Redis).")

# 2. Actualizar router.py para pasar redis_client al logger
router_path = "SOBERANO_03_NEXUS/core/router.py"
with open(router_path, "r", encoding="utf-8") as f:
    router_content = f.read()

old_call = """        # Registro soberano en bitácora (Art. 5)
        registrar_en_bitacora(
            chat_id=str(chat_id),
            accion=f"Consulta rol: {rol}",
            herramientas_usadas=["call_ia"],
            resultado_resumen=f"P: {text[:80]}... | R: {respuesta[:80]}..."
        )"""

new_call = """        # Registro soberano en bitácora (Art. 5)
        registrar_en_bitacora(
            chat_id=str(chat_id),
            accion=f"Consulta rol: {rol}",
            herramientas_usadas=["call_ia"],
            resultado_resumen=f"P: {text[:80]}... | R: {respuesta[:80]}...",
            redis_client=redis_client
        )"""

if old_call in router_content:
    router_content = router_content.replace(old_call, new_call)
    print("✅ router.py: Actualizado para pasar redis_client al logger.")

with open(router_path, "w", encoding="utf-8") as f:
    f.write(router_content)

print("\n📝 Preparando validación de sintaxis...")
EOF

# ==========================================
# VALIDACIÓN DE SINTAXIS
# ==========================================
echo ""
echo "🔍 VALIDANDO SINTAXIS..."
python3 -m py_compile SOBERANO_03_NEXUS/core/memory_logger.py && echo "✅ memory_logger.py: SINTAXIS CORRECTA" || echo "❌ ERROR"
python3 -m py_compile SOBERANO_03_NEXUS/core/router.py && echo "✅ router.py: SINTAXIS CORRECTA" || echo "❌ ERROR"
echo ""
echo "=================================================="
echo "✅ CORRECCIÓN DE COMPATIBILIDAD CON VERCEL APLICADA."
echo "El bot ya no colapsará al intentar escribir en disco."
echo ""
echo "Ejecute para desplegar:"
echo ""
echo "git add SOBERANO_03_NEXUS/core/memory_logger.py SOBERANO_03_NEXUS/core/router.py"
echo "git commit -m '[FIX] Compatibilidad con sistema de archivos de solo lectura de Vercel (Fallback a Redis)'"
echo "git push origin soberano-v1"
echo "=================================================="
git add SOBERANO_03_NEXUS/core/memory_logger.py SOBERANO_03_NEXUS/core/router.py
git commit -m '[FIX] Compatibilidad con sistema de archivos de solo lectura de Vercel (Fallback a Redis)'
git push origin soberano-v1
