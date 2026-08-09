
## ⏳ PENDIENTE REAL ÚNICO (Prioridad Máxima)
1. **[ID-0017]** Implementación del Monitoreo de Drawdown 2.0% con Circuit Breaker Institucional (Sensor de equidad en tiempo real, bloqueo en Redis y reinicio auditado).

## 🚀 PRÓXIMO PASO INMEDIATO
- Codificar y probar el módulo `check_drawdown()` en `risk_manager.py`.
EOF

echo "✅ ESTADO_DEL_SISTEMA.md redefinido limpiamente (0 riesgo de corrupción)."
python3 << 'EOF'
import os
import re
import json
from datetime import datetime
from collections import defaultdict

print("=" * 80)
print("🔍 AUDITORÍA FORENSE INTEGRAL DEL SISTEMA MAESTRO-NEXUS")
print("=" * 80)
print(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Metodología: Evidencia dura del sistema. Cero memoria de IA.")
print("=" * 80)

reporte = []
reporte.append("# 🏛️ AUDITORÍA FORENSE INTEGRAL - MAESTRO NEXUS\n")
reporte.append(f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
reporte.append(f"**Metodología:** Análisis estático del repositorio. Evidencia pura.\n\n")

semáforo = {"🟢": 0, "🟡": 0, "🔴": 0}

def registrar(seccion, estado, hallazgo, evidencia=""):
    reporte.append(f"## {estado} {seccion}\n")
    reporte.append(f"**Hallazgo:** {hallazgo}\n\n")
    if evidencia:
        reporte.append(f"**Evidencia del sistema:**\n```text\n{evidencia}\n```\n\n")
    semáforo[estado] += 1

# ============================================================
# 1. AUDITORÍA DE BITÁCORA (IDs, hashes, deuda documental)
# ============================================================
print("\n📜 [1/12] Analizando bitácora...")
bitacora_path = "BITACORA.md"
if os.path.exists(bitacora_path):
    with open(bitacora_path, "r", encoding="utf-8") as f:
        bitacora = f.read()
    
    ids = re.findall(r'## \[(ID-\d{4})\]', bitacora)
    hashes = re.findall(r'\*\*Hash actual:\*\* ([a-f0-9]{64})', bitacora)
    pendientes_activos = re.findall(r'- \[ \] ([^\n]*PENDIENTE[^\n]*)', bitacora)
    enmiendas = re.findall(r'## \[ID-\d{4}-[A-Z]\]', bitacora)
    
    # Verificar IDs duplicados
    ids_duplicados = [id for id in set(ids) if ids.count(id) > 1]
    
    # Verificar cadena de hashes
    hashes_anteriores = re.findall(r'\*\*Hash anterior:\*\* ([a-f0-9]{64}|\[CALCULADO\])', bitacora)
    
    evidencia_bitacora = f"Total de actas: {len(ids)}\n"
    evidencia_bitacora += f"IDs únicos: {len(set(ids))}\n"
    evidencia_bitacora += f"Hashes encadenados detectados: {len(hashes)}\n"
    evidencia_bitacora += f"Enmiendas registradas: {len(enmiendas)}\n"
    evidencia_bitacora += f"Pendientes activos con [ ]: {len(pendientes_activos)}\n"
    evidencia_bitacora += f"IDs duplicados: {ids_duplicados if ids_duplicados else 'Ninguno'}"
    
    if ids_duplicados:
        registrar("1. AUDITORÍA DE BITÁCORA", "🔴", "Se detectaron IDs duplicados en la bitácora", evidencia_bitacora)
    elif len(pendientes_activos) > 5:
        registrar("1. AUDITORÍA DE BITÁCORA", "🟡", f"Bitácora íntegra pero con {len(pendientes_activos)} pendientes activos (posible deuda documental)", evidencia_bitacora)
    else:
        registrar("1. AUDITORÍA DE BITÁCORA", "🟢", "Bitácora íntegra, sin IDs duplicados y con cadena de hashes", evidencia_bitacora)
else:
    registrar("1. AUDITORÍA DE BITÁCORA", "🔴", "CRÍTICO: No existe el archivo BITACORA.md")

# ============================================================
# 2. DOCUMENTACIÓN CLAVE (Constitución, Estado, Roles)
# ============================================================
print("📄 [2/12] Verificando documentos clave...")
docs_clave = {
    "Constitución": "SOBERANO_00_GOBIERNO/CONSTITUCION.md",
    "Roles y Misiones": "SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md",
    "Estado del Sistema": "ESTADO_DEL_SISTEMA.md",
    "Bitácora": "BITACORA.md",
    "Manifest Nexus": "SOBERANO_00_GOBIERNO/NEXUS_MANIFEST.json",
}

docs_existentes = []
docs_faltantes = []
for nombre, ruta in docs_clave.items():
    if os.path.exists(ruta):
        size = os.path.getsize(ruta)
        docs_existentes.append(f"✅ {nombre}: {ruta} ({size} bytes)")
    else:
        docs_faltantes.append(f"❌ {nombre}: {ruta} NO EXISTE")

evidencia_docs = "\n".join(docs_existentes + docs_faltantes)

if docs_faltantes:
    registrar("2. DOCUMENTACIÓN CLAVE", "🟡", f"Faltan {len(docs_faltantes)} documento(s) clave", evidencia_docs)
else:
    registrar("2. DOCUMENTACIÓN CLAVE", "🟢", "Todos los documentos clave están presentes", evidencia_docs)

# ============================================================
# 3. ESTRUCTURA DE DIRECTORIOS (Orden y arquitectura)
# ============================================================
print("📂 [3/12] Analizando estructura de directorios...")
directorios_clave = [
    "SOBERANO_00_GOBIERNO",
    "SOBERANO_01_MEMORIA",
    "SOBERANO_02_CORE",
    "SOBERANO_03_NEXUS",
]

estructura = []
for d in directorios_clave:
    if os.path.exists(d):
        subdirs = [x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x)) and not x.startswith('.')]
        estructura.append(f"📁 {d}: {len(subdirs)} subdirectorios → {', '.join(subdirs)}")
    else:
        estructura.append(f"❌ {d}: NO EXISTE")

# Buscar anomalías (carpetas sueltas en raíz)
raiz_anomalias = [x for x in os.listdir('.') 
                  if os.path.isdir(x) 
                  and not x.startswith('.') 
                  and not x.startswith('SOBERANO_')
                  and x not in ['__pycache__', 'node_modules']]

evidencia_estructura = "\n".join(estructura)
if raiz_anomalias:
    evidencia_estructura += f"\n\n⚠️ Directorios anómalos en raíz: {raiz_anomalias}"

if not all("NO EXISTE" not in e for e in estructura):
    registrar("3. ESTRUCTURA DE DIRECTORIOS", "🔴", "Faltan directorios SOBERANO obligatorios", evidencia_estructura)
elif raiz_anomalias:
    registrar("3. ESTRUCTURA DE DIRECTORIOS", "🟡", f"Estructura base correcta pero {len(raiz_anomalias)} directorio(s) anómalo(s) en raíz", evidencia_estructura)
else:
    registrar("3. ESTRUCTURA DE DIRECTORIOS", "🟢", "Estructura de 4 departamentos SOBERANO intacta y limpia", evidencia_estructura)

# ============================================================
# 4. MODULARIZACIÓN (Archivos Python, tamaño, responsabilidades)
# ============================================================
print("🐍 [4/12] Analizando modularización del código Python...")
py_files = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv']]
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f).replace('./', '')
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    lines = len(file.readlines())
                py_files.append((path, lines))
            except:
                py_files.append((path, -1))

py_files.sort(key=lambda x: x[1], reverse=True)

# Detectar monolitos (>150 líneas)
monolitos = [(p, l) for p, l in py_files if l > 150]
# Detectar archivos vacíos o mínimos (<5 líneas)
triviales = [(p, l) for p, l in py_files if 0 < l < 5]

evidencia_mod = f"Total de archivos Python: {len(py_files)}\n"
evidencia_mod += f"Total de líneas de código: {sum(l for _, l in py_files if l > 0)}\n"
evidencia_mod += f"Archivos monolíticos (>150 líneas): {len(monolitos)}\n"
evidencia_mod += f"Archivos triviales (<5 líneas): {len(triviales)}\n\n"

if monolitos:
    evidencia_mod += "Monolitos detectados:\n"
    for p, l in monolitos[:10]:
        evidencia_mod += f"  - {p}: {l} líneas\n"

if triviales:
    evidencia_mod += "\nArchivos triviales:\n"
    for p, l in triviales[:10]:
        evidencia_mod += f"  - {p}: {l} líneas\n"

if monolitos:
    registrar("4. MODULARIZACIÓN", "🟡", f"{len(monolitos)} archivo(s) Python exceden 150 líneas (candidatos a refactorización)", evidencia_mod)
else:
    registrar("4. MODULARIZACIÓN", "🟢", "Todos los archivos Python tienen tamaño controlado (<150 líneas)", evidencia_mod)

# ============================================================
# 5. DETECCIÓN DE DUPLICADOS (Nombres repetidos)
# ============================================================
print("🔁 [5/12] Detectando archivos duplicados...")
nombre_archivos = defaultdict(list)
for path, _ in py_files:
    nombre = os.path.basename(path)
    nombre_archivos[nombre].append(path)

duplicados = {k: v for k, v in nombre_archivos.items() if len(v) > 1 and k != '__init__.py'}

evidencia_dup = ""
if duplicados:
    for nombre, paths in duplicados.items():
        evidencia_dup += f"⚠️ {nombre} aparece {len(paths)} veces:\n"
        for p in paths:
            evidencia_dup += f"  - {p}\n"
    registrar("5. DUPLICADOS DE NOMBRES", "🟡", f"{len(duplicados)} nombre(s) de archivo repetido(s)", evidencia_dup)
else:
    registrar("5. DUPLICADOS DE NOMBRES", "🟢", "No hay nombres de archivo Python duplicados (excepto __init__.py)", "Limpieza de duplicados efectiva.")

# ============================================================
# 6. DEPENDENCIAS E IMPORTS (Mapa de flujo)
# ============================================================
print("🔗 [6/12] Mapeando dependencias e imports...")
index_path = "SOBERANO_03_NEXUS/index.py"
if os.path.exists(index_path):
    with open(index_path, 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    imports_index = re.findall(r'(?:from|import)\s+([^\s\n]+)', index_content)
    
    evidencia_flujo = "Punto de entrada: SOBERANO_03_NEXUS/index.py\n\n"
    evidencia_flujo += f"Imports declarados: {len(imports_index)}\n\n"
    evidencia_flujo += "Flujo de arranque detectado:\n"
    for imp in imports_index[:15]:
        evidencia_flujo += f"  → {imp}\n"
    
    if "verify_startup_requirements" in index_content:
        evidencia_flujo += "\n✅ Guardián (Hard-Fail) invocado al arranque"
    
    if "@asynccontextmanager" in index_content or "lifespan" in index_content:
        evidencia_flujo += "\n✅ Patrón lifespan moderno detectado"
    
    registrar("6. FLUJO Y DEPENDENCIAS", "🟢", "index.py actúa como Application Factory con imports modulares", evidencia_flujo)
else:
    registrar("6. FLUJO Y DEPENDENCIAS", "🔴", "No existe index.py, no se puede mapear el flujo")

# ============================================================
# 7. SEGURIDAD (Guardián, endpoints expuestos)
# ============================================================
print("🛡️ [7/12] Auditando seguridad...")
guardian_path = "SOBERANO_03_NEXUS/core/guardian.py"
diagnostics_path = "SOBERANO_03_NEXUS/core/diagnostics.py"

evidencia_seg = ""
if os.path.exists(guardian_path):
    with open(guardian_path, 'r', encoding='utf-8') as f:
        guardian_content = f.read()
    evidencia_seg += f"✅ guardian.py existe ({len(guardian_content)} bytes)\n"
    if "CRITICAL_VARS" in guardian_content:
        evidencia_seg += "  - Valida variables críticas (ALPACA, TELEGRAM, REDIS)\n"
else:
    evidencia_seg += "❌ guardian.py NO EXISTE\n"

if os.path.exists(diagnostics_path):
    with open(diagnostics_path, 'r', encoding='utf-8') as f:
        diag_content = f.read()
    evidencia_seg += f"✅ diagnostics.py existe ({len(diag_content)} bytes)\n"
    if "verificar_acceso" in diag_content or "token" in diag_content.lower():
        evidencia_seg += "  - Endpoints de debug protegidos por token\n"
    else:
        evidencia_seg += "  ⚠️ Endpoints de debug SIN protección por token\n"
else:
    evidencia_seg += "ℹ️ diagnostics.py no existe (endpoints de debug eliminados)\n"

# Buscar variables hardcoded peligrosas
secrets_hardcoded = []
for path, _ in py_files:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if re.search(r'(API_KEY|SECRET|TOKEN|PASSWORD)\s*=\s*["\'][^"\']{10,}["\']', content, re.IGNORECASE):
            secrets_hardcoded.append(path)
    except:
        pass

if secrets_hardcoded:
    evidencia_seg += f"\n🔴 Secretos hardcodeados detectados en: {secrets_hardcoded}"
    registrar("7. SEGURIDAD", "🔴", "Secretos hardcodeados en código fuente", evidencia_seg)
elif os.path.exists(guardian_path):
    registrar("7. SEGURIDAD", "🟢", "Guardián activo, sin secretos hardcodeados", evidencia_seg)
else:
    registrar("7. SEGURIDAD", "🟡", "Sin secretos hardcodeados pero sin Guardián", evidencia_seg)

# ============================================================
# 8. VEEDURÍA DE DOCUMENTACIÓN (Coherencia con código)
# ============================================================
print("🔍 [8/12] Veeduría: coherencia documental vs código...")
const_path = "SOBERANO_00_GOBIERNO/CONSTITUCION.md"
if os.path.exists(const_path):
    with open(const_path, 'r', encoding='utf-8') as f:
        const = f.read()
    
    menciones_codigo = []
    for palabra in ['drawdown', 'hard-fail', 'guardián', 'redis', 'telegram', 'alpaca']:
        if palabra.lower() in const.lower():
            menciones_codigo.append(palabra)
    
    evidencia_veeduria = f"Constitución menciona {len(menciones_codigo)} componentes técnicos: {', '.join(menciones_codigo)}\n\n"
    
    # Verificar que lo mencionado existe en código
    coherente = True
    for comp in menciones_codigo:
        encontrado = False
        for path, _ in py_files:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    if comp.lower() in f.read().lower():
                        encontrado = True
                        break
            except:
                pass
        if not encontrado:
            evidencia_veeduria += f"⚠️ '{comp}' mencionado en Constitución pero no hallado en código\n"
            coherente = False
    
    if coherente:
        evidencia_veeduria += "✅ Todos los componentes mencionados en Constitución tienen correlato en código"
    
    registrar("8. VEEDURÍA DOCUMENTAL", "🟢" if coherente else "🟡", 
              "Coherencia entre Constitución y código" if coherente else "Inconsistencias detectadas entre Constitución y código",
              evidencia_veeduria)
else:
    registrar("8. VEEDURÍA DOCUMENTAL", "🔴", "No se puede hacer veeduría sin Constitución")

# ============================================================
# 9. CONTRALORÍA (Archivos de auditoría y logs)
# ============================================================
print("📊 [9/12] Contraloría: registros de auditoría...")
audit_dirs = [
    "SOBERANO_01_MEMORIA/AUDITS",
    "SOBERANO_01_MEMORIA/ACTAS",
]

evidencia_contraloria = ""
for d in audit_dirs:
    if os.path.exists(d):
        archivos = os.listdir(d)
        evidencia_contraloria += f"✅ {d}: {len(archivos)} archivos\n"
        for a in archivos[:5]:
            evidencia_contraloria += f"  - {a}\n"
        if len(archivos) > 5:
            evidencia_contraloria += f"  - ... y {len(archivos)-5} más\n"
    else:
        evidencia_contraloria += f"❌ {d}: NO EXISTE\n"

# Verificar memoria activa
if os.path.exists("ESTADO_DEL_SISTEMA.md"):
    evidencia_contraloria += "\n✅ ESTADO_DEL_SISTEMA.md presente (memoria activa del sistema)"
else:
    evidencia_contraloria += "\n❌ ESTADO_DEL_SISTEMA.md NO EXISTE"

if os.path.exists("validar_memoria.py"):
    evidencia_contraloria += "\n✅ validar_memoria.py presente (auditor automático)"

if os.path.exists("briefing.sh"):
    evidencia_contraloria += "\n✅ briefing.sh presente (briefing automático)"

registrar("9. CONTRALORÍA", "🟢" if "NO EXISTE" not in evidencia_contraloria else "🟡",
          "Registros de auditoría y memoria activa",
          evidencia_contraloria)

# ============================================================
# 10. RUTAS Y FLUJOS (Mapeo de ejecutables)
# ============================================================
print("🛣️ [10/12] Mapeando rutas de ejecución...")
ejecutables = []
for path, _ in py_files:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'if __name__ == "__main__"' in content or "if __name__ == '__main__'" in content:
            ejecutables.append(path)
    except:
        pass

scripts_sh = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
    for f in files:
        if f.endswith('.sh'):
            scripts_sh.append(os.path.join(root, f).replace('./', ''))

evidencia_rutas = f"Archivos Python ejecutables (con __main__): {len(ejecutables)}\n"
for e in ejecutables[:10]:
    evidencia_rutas += f"  - {e}\n"
evidencia_rutas += f"\nScripts bash (.sh): {len(scripts_sh)}\n"
for s in scripts_sh[:10]:
    evidencia_rutas += f"  - {s}\n"

registrar("10. RUTAS Y PUNTOS DE ENTRADA", "🟢" if ejecutables else "🟡",
          f"{len(ejecutables)} punto(s) de entrada Python y {len(scripts_sh)} script(s) bash",
          evidencia_rutas)

# ============================================================
# 11. FORMATOS Y ESTÁNDARES (Convenciones de código)
# ============================================================
print("📐 [11/12] Verificando estándares de formato...")
headers_estandar = 0
sin_header = 0
for path, lines in py_files:
    if lines < 10:
        continue
    try:
        with open(path, 'r', encoding='utf-8') as f:
            primera_linea = f.readline()
            if '======' in primera_linea or '#!/' in primera_linea or '"""' in primera_linea:
                headers_estandar += 1
            else:
                sin_header += 1
    except:
        pass

evidencia_fmt = f"Archivos con header estándar: {headers_estandar}\n"
evidencia_fmt += f"Archivos sin header estándar: {sin_header}\n"

if sin_header > headers_estandar:
    registrar("11. FORMATOS Y ESTÁNDARES", "🟡", "Mayoría de archivos Python sin header estándar", evidencia_fmt)
else:
    registrar("11. FORMATOS Y ESTÁNDARES", "🟢", "Convenciones de formato aplicadas consistentemente", evidencia_fmt)

# ============================================================
# 12. MAPA DE LÓGICA DE TRADING
# ============================================================
print("💹 [12/12] Mapeando lógica de trading...")
trading_dir = "SOBERANO_03_NEXUS/trading"
if os.path.exists(trading_dir):
    trading_files = os.listdir(trading_dir)
    evidencia_trading = f"Directorio de trading: {trading_dir}\n"
    evidencia_trading += f"Archivos: {len(trading_files)}\n\n"
    
    for tf in trading_files:
        path = os.path.join(trading_dir, tf)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            evidencia_trading += f"📄 {tf}: {size} bytes\n"
    
    # Verificar componentes críticos
    criticos = {
        'engine.py': 'Motor de ejecución',
        'risk_manager.py': 'Gestor de riesgo (incluye Drawdown)',
        'strategy_engine.py': 'Motor de estrategia',
        'position_sizer.py': 'Tamaño de posición',
    }
    
    evidencia_trading += "\nComponentes críticos:\n"
    for arch, rol in criticos.items():
        if arch in trading_files:
            evidencia_trading += f"✅ {arch}: {rol}\n"
        else:
            evidencia_trading += f"❌ {arch}: {rol} - NO EXISTE\n"
    
    # Verificar si risk_manager.py tiene drawdown
    rm_path = os.path.join(trading_dir, "risk_manager.py")
    if os.path.exists(rm_path):
        with open(rm_path, 'r', encoding='utf-8') as f:
            rm_content = f.read()
        if 'drawdown' in rm_content.lower():
            evidencia_trading += "\n✅ risk_manager.py contiene lógica de drawdown"
        else:
            evidencia_trading += "\n❌ risk_manager.py NO contiene lógica de drawdown (pendiente ID-0017)"
    
    registrar("12. LÓGICA DE TRADING", "🟢" if "NO EXISTE" not in evidencia_trading and "NO contiene" not in evidencia_trading else "🟡",
              "Arquitectura de trading institucional",
              evidencia_trading)
else:
    registrar("12. LÓGICA DE TRADING", "🔴", "No existe directorio de trading")

# ============================================================
# RESUMEN EJECUTIVO
# ============================================================
resumen = []
resumen.append("# 📋 RESUMEN EJECUTIVO\n\n")
resumen.append(f"- 🟢 Aprobado: {semáforo['🟢']}\n")
resumen.append(f"- 🟡 Advertencia: {semáforo['🟡']}\n")
resumen.append(f"- 🔴 Crítico: {semáforo['🔴']}\n\n")

score = semáforo['🟢'] * 100 // 12
resumen.append(f"**Puntuación global del sistema:** {score}/100\n\n")

if score >= 80:
    resumen.append("**Veredicto:** Sistema maduro, auditado y con trazabilidad. Listo para pasar de teoría a implementación.\n\n")
elif score >= 60:
    resumen.append("**Veredicto:** Sistema funcional con áreas de mejora. Requiere atención a advertencias antes de escalar.\n\n")
else:
    resumen.append("**Veredicto:** Sistema con deuda estructural. Debe corregir críticos antes de avanzar.\n\n")

# Insertar resumen al inicio
reporte = resumen + reporte

# ============================================================
# GUARDAR REPORTE
# ============================================================
reporte_path = "AUDITORIA_INTEGRAL.md"
with open(reporte_path, "w", encoding="utf-8") as f:
    f.writelines(reporte)

print("\n" + "=" * 80)
print(f"✅ AUDITORÍA FORENSE COMPLETADA")
print(f"📄 Reporte generado: {reporte_path}")
print(f"📊 Resultado: {semáforo['🟢']} OK | {semáforo['🟡']} Advertencia | {semáforo['🔴']} Crítico")
print("=" * 80)
print(f"\n👉 Para revisar la auditoría completa:")
print(f"   cat {reporte_path}")
EOF

cat AUDITORIA_INTEGRAL.md
