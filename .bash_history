    return resultado
"""

# Reemplazar el endpoint anterior si existe, o agregarlo
if "@app.get(\"/debug-alpaca\")" in content:
    # Buscar y reemplazar todo el bloque anterior del endpoint
    import re
    content = re.sub(
        r'@app\.get\("/debug-alpaca"\).*?(?=\n@app\.get|\nif __name__ == "__main__":)',
        nuevo_debug,
        content,
        flags=re.DOTALL
    )
else:
    content = content.replace(
        'if __name__ == "__main__":',
        nuevo_debug + '\nif __name__ == "__main__":'
    )

with open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Endpoint /debug-alpaca actualizado con prueba HTTP directa.")

print("\n📤 Enviando a GitHub...")
subprocess.run(["git", "add", index_path], capture_output=True)
subprocess.run(["git", "commit", "-m", "[AUDIT] Prueba HTTP directa desde Railway sin librerías"], capture_output=True)
push_result = subprocess.run(["git", "push", "origin", "soberano-v1"], capture_output=True, text=True)

if push_result.returncode == 0:
    print("✅ Desplegado. Railway reconstruirá automáticamente.")
else:
    print(f"⚠️ Advertencia: {push_result.stderr}")

print("\n" + "=" * 80)
print("⏳ ESPERE 2 MINUTOS A QUE RAILWAY ESTÉ EN VERDE (Active)")
print("LUEGO VISITE: https://maestrotrading-production-c2db.up.railway.app/debug-alpaca")
print("=" * 80)
EOF

python3 << 'EOF'
import os
import subprocess

print("=" * 80)
print("🔍 INYECTANDO ENDPOINT DE DIAGNÓSTICO DUAL (PAPER + LIVE)")
print("=" * 80)

index_path = "SOBERANO_03_NEXUS/index.py"
with open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

# Nuevo endpoint que prueba AMBOS endpoints
dual_debug = """
@app.get("/debug-alpaca-dual")
async def debug_alpaca_dual():
    import httpx
    
    api_key = os.getenv("ALPACA_API_KEY", "").strip()
    secret_key = os.getenv("ALPACA_SECRET_KEY", "").strip()
    
    resultado = {
        "servidor": "Railway (En vivo)",
        "variables_saneadas": {
            "API_KEY_longitud": len(api_key),
            "API_KEY_repr": repr(api_key[:10]) + "..." if api_key else "VACIO",
            "SECRET_KEY_longitud": len(secret_key),
        },
        "prueba_paper": "Pendiente...",
        "prueba_live": "Pendiente...",
        "diagnostico_final": "Pendiente..."
    }
    
    if not api_key or not secret_key:
        resultado["diagnostico_final"] = "FALLIDO: Variables vacías"
        return resultado
    
    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key
    }
    
    # Probar Paper Trading
    try:
        async with httpx.AsyncClient() as client:
            resp_paper = await client.get("https://paper-api.alpaca.markets/v2/account", headers=headers, timeout=10.0)
            resultado["prueba_paper"] = {
                "status_code": resp_paper.status_code,
                "respuesta": resp_paper.text[:200]
            }
    except Exception as e:
        resultado["prueba_paper"] = f"ERROR: {str(e)}"
    
    # Probar Live Trading
    try:
        async with httpx.AsyncClient() as client:
            resp_live = await client.get("https://api.alpaca.markets/v2/account", headers=headers, timeout=10.0)
            resultado["prueba_live"] = {
                "status_code": resp_live.status_code,
                "respuesta": resp_live.text[:200]
            }
    except Exception as e:
        resultado["prueba_live"] = f"ERROR: {str(e)}"
    
    # Diagnóstico final
    paper_ok = isinstance(resultado["prueba_paper"], dict) and resultado["prueba_paper"].get("status_code") == 200
    live_ok = isinstance(resultado["prueba_live"], dict) and resultado["prueba_live"].get("status_code") == 200
    
    if paper_ok and not live_ok:
        resultado["diagnostico_final"] = "✅ CLAVES DE PAPER TRADING - Use endpoint paper-api"
    elif live_ok and not paper_ok:
        resultado["diagnostico_final"] = "⚠️ CLAVES DE LIVE TRADING - Las claves son de cuenta real, no paper"
    elif paper_ok and live_ok:
        resultado["diagnostico_final"] = "❌ ANOMALÍA: Ambas cuentas aceptan las claves"
    else:
        resultado["diagnostico_final"] = "❌ CLAVES INVÁLIDAS: Ninguna cuenta acepta estas credenciales"
    
    return resultado
"""

# Insertar o reemplazar el endpoint
if "@app.get(\"/debug-alpaca-dual\")" in content:
    import re
    content = re.sub(
        r'@app\.get\("/debug-alpaca-dual"\).*?(?=\n@app\.get|\nif __name__ == "__main__":)',
        dual_debug,
        content,
        flags=re.DOTALL
    )
else:
    content = content.replace(
        'if __name__ == "__main__":',
        dual_debug + '\nif __name__ == "__main__":'
    )

with open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Endpoint /debug-alpaca-dual inyectado.")

print("\n📤 Enviando a GitHub...")
subprocess.run(["git", "add", index_path], capture_output=True)
subprocess.run(["git", "commit", "-m", "[AUDIT] Endpoint dual para determinar tipo de clave (paper vs live)"], capture_output=True)
push_result = subprocess.run(["git", "push", "origin", "soberano-v1"], capture_output=True, text=True)

if push_result.returncode == 0:
    print("✅ Desplegado. Railway reconstruirá automáticamente.")
else:
    print(f"⚠️ Advertencia: {push_result.stderr}")

print("\n" + "=" * 80)
print("⏳ ESPERE 2 MINUTOS A QUE RAILWAY ESTÉ EN VERDE (Active)")
print("LUEGO VISITE: https://maestrotrading-production-c2db.up.railway.app/debug-alpaca-dual")
print("=" * 80)
EOF

python3 << 'EOF'
import os
import subprocess

print("=" * 80)
print("🔧 APLICANDO SANEAMIENTO AUTOMÁTICO A CONFIG.PY")
print("=" * 80)

config_path = "SOBERANO_03_NEXUS/config.py"
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Reemplazar las líneas de ALPACA_API_KEY y ALPACA_SECRET_KEY para agregar .strip()
    content = content.replace(
        'ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")',
        'ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "").strip()'
    )
    content = content.replace(
        'ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")',
        'ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "").strip()'
    )
    
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ config.py actualizado con .strip() automático.")
else:
    print("❌ config.py no encontrado.")

print("\n📤 Enviando a GitHub...")
subprocess.run(["git", "add", config_path], capture_output=True)
subprocess.run(["git", "commit", "-m", "[FIX] Saneamiento automático de variables Alpaca con .strip()"], capture_output=True)
push_result = subprocess.run(["git", "push", "origin", "soberano-v1"], capture_output=True, text=True)

if push_result.returncode == 0:
    print("✅ Desplegado.")
else:
    print(f"⚠️ Advertencia: {push_result.stderr}")

print("=" * 80)
EOF

python3 << 'EOF'
import os
import json
from datetime import datetime
from pathlib import Path

print("=" * 80)
print("🔍 AUDITORÍA CONSTITUCIONAL COMPLETA DEL SISTEMA")
print("=" * 80)
print(f"Fecha de auditoría: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Configuración de búsqueda
BUSQUEDAS = {
    "nombres_archivo": [
        "constitucion", "ley", "norma", "acta", "biblia", "manifiesto",
        "manifest", "dossier", "gobernanza", "gobierno", "reglamento",
        "protocolo", "directiva", "decreto", "orden", "resolucion"
    ],
    "palabras_clave_contenido": [
        "artículo", "articulo", "ley", "norma", "constitución", "constitucion",
        "gobernanza", "soberanía", "soberania", "directorial", "parlamento",
        "nexus", "manifiesto", "acta de", "promulgación", "promulgacion"
    ],
    "extensiones": [".md", ".txt", ".json", ".yaml", ".yml", ".sh"]
}

# Resultados
resultados = {
    "archivos_encontrados": [],
    "archivos_por_carpeta": {},
    "clasificacion": {
        "util_vigente": [],
        "duplicado": [],
        "obsoleto": [],
        "backup_manual": [],
        "script_operativo": []
    },
    "metadata_extraida": []
}

# Función para clasificar archivos
def clasificar_archivo(ruta, nombre):
    nombre_lower = nombre.lower()
    
    # Backup manual
    if "backup" in ruta.lower() or "pre-enmienda" in nombre_lower:
        return "backup_manual"
    
    # Script operativo
    if nombre_lower.endswith(".sh") or "script" in ruta.lower():
        return "script_operativo"
    
    # Obsoleto
    if "legacy" in ruta.lower() or "pendiente" in nombre_lower:
        return "obsoleto"
    
    # Constitución principal
    if nombre_lower == "constitucion.md" and "00-gobierno" in ruta.lower():
        return "util_vigente"
    
    # Leyes y normas en dossier (probablemente duplicadas)
    if "dossier/constitucion" in ruta.lower():
        return "duplicado"
    
    # Biblia (probablemente duplicada)
    if "biblia" in nombre_lower:
        return "duplicado"
    
    # Por defecto, útil
    return "util_vigente"

# Función para extraer metadata
def extraer_metadata(ruta, contenido):
    metadata = {
        "ruta": ruta,
        "titulo": "",
        "version": "",
        "fecha": "",
        "estado": "",
        "tipo": ""
    }
    
    # Buscar título
    for linea in contenido.split('\n')[:10]:
        if linea.startswith('#'):
            metadata["titulo"] = linea.replace('#', '').strip()
            break
    
    # Buscar versión
    if "versión:" in contenido.lower() or "version:" in contenido.lower():
        for linea in contenido.split('\n')[:20]:
            if "versión" in linea.lower() or "version" in linea.lower():
                metadata["version"] = linea.split(':')[-1].strip()
                break
    
    # Buscar fecha
    if "fecha:" in contenido.lower():
        for linea in contenido.split('\n')[:20]:
            if "fecha" in linea.lower():
                metadata["fecha"] = linea.split(':')[-1].strip()
                break
    
    # Buscar estado
    if "estado:" in contenido.lower():
        for linea in contenido.split('\n')[:20]:
            if "estado" in linea.lower():
                metadata["estado"] = linea.split(':')[-1].strip()
                break
    
    # Determinar tipo
    nombre = os.path.basename(ruta).lower()
    if "constitucion" in nombre:
        metadata["tipo"] = "Constitución"
    elif nombre.startswith("ley-"):
        metadata["tipo"] = "Ley"
    elif nombre.startswith("norma-"):
        metadata["tipo"] = "Norma"
    elif nombre.startswith("acta"):
        metadata["tipo"] = "Acta"
    elif "biblia" in nombre:
        metadata["tipo"] = "Biblia (Documento Maestro)"
    else:
        metadata["tipo"] = "Otro"
    
    return metadata

# Escaneo del repositorio
print("\n📂 ESCANEANDO REPOSITORIO...")
print("-" * 80)

for root, dirs, files in os.walk('.'):
    # Ignorar directorios de sistema
    dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'node_modules']]
    
    for file in files:
        ruta_completa = os.path.join(root, file)
        nombre_lower = file.lower()
        
        # Verificar si el nombre coincide con búsquedas
        coincide_nombre = any(busq in nombre_lower for busq in BUSQUEDAS["nombres_archivo"])
        
        # Verificar extensión
        extension_ok = any(nombre_lower.endswith(ext) for ext in BUSQUEDAS["extensiones"])
        
        if coincide_nombre and extension_ok:
            try:
                with open(ruta_completa, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Verificar si el contenido tiene palabras clave
                coincide_contenido = any(palabra in contenido.lower() for palabra in BUSQUEDAS["palabras_clave_contenido"])
                
                if coincide_contenido or coincide_nombre:
                    # Clasificar
                    clasificacion = clasificar_archivo(ruta_completa, file)
                    
                    # Extraer metadata
                    metadata = extraer_metadata(ruta_completa, contenido)
                    
                    # Agregar a resultados
                    resultados["archivos_encontrados"].append({
                        "ruta": ruta_completa,
                        "nombre": file,
                        "tamano_kb": round(len(contenido) / 1024, 2),
                        "lineas": len(contenido.split('\n')),
                        "clasificacion": clasificacion
                    })
                    
                    resultados["clasificacion"][clasificacion].append(ruta_completa)
                    resultados["metadata_extraida"].append(metadata)
                    
                    # Contar por carpeta
                    carpeta = os.path.dirname(ruta_completa)
                    if carpeta not in resultados["archivos_por_carpeta"]:
                        resultados["archivos_por_carpeta"][carpeta] = []
                    resultados["archivos_por_carpeta"][carpeta].append(file)
                    
            except Exception as e:
                print(f"   ⚠️ Error leyendo {ruta_completa}: {e}")

# Generar reporte
print("\n" + "=" * 80)
print("📊 REPORTE DE AUDITORÍA CONSTITUCIONAL")
print("=" * 80)

print(f"\n📁 TOTAL DE ARCHIVOS ENCONTRADOS: {len(resultados['archivos_encontrados'])}")

print("\n📂 DISTRIBUCIÓN POR CARPETA:")
for carpeta, archivos in sorted(resultados["archivos_por_carpeta"].items()):
    print(f"   {carpeta}: {len(archivos)} archivos")

print("\n🏷️ CLASIFICACIÓN:")
print(f"   ✅ Útil y Vigente: {len(resultados['clasificacion']['util_vigente'])} archivos")
print(f"   ⚠️ Duplicado: {len(resultados['clasificacion']['duplicado'])} archivos")
print(f"   ❌ Obsoleto: {len(resultados['clasificacion']['obsoleto'])} archivos")
print(f"   💾 Backup Manual: {len(resultados['clasificacion']['backup_manual'])} archivos")
print(f"   🔧 Script Operativo: {len(resultados['clasificacion']['script_operativo'])} archivos")

print("\n📋 DETALLE DE ARCHIVOS ÚTILES Y VIGENTES:")
for archivo in resultados["archivos_encontrados"]:
    if archivo["clasificacion"] == "util_vigente":
        print(f"   ✅ {archivo['ruta']} ({archivo['tamano_kb']} KB, {archivo['lineas']} líneas)")

print("\n⚠️ DETALLE DE ARCHIVOS DUPLICADOS:")
for archivo in resultados["archivos_encontrados"]:
    if archivo["clasificacion"] == "duplicado":
        print(f"   ⚠️ {archivo['ruta']} ({archivo['tamano_kb']} KB)")

print("\n💾 DETALLE DE BACKUPS MANUALES:")
for archivo in resultados["archivos_encontrados"]:
    if archivo["clasificacion"] == "backup_manual":
        print(f"   💾 {archivo['ruta']} ({archivo['tamano_kb']} KB)")

print("\n📜 METADATA EXTRAÍDA (Primeros 10 archivos):")
for meta in resultados["metadata_extraida"][:10]:
    print(f"   📄 {meta['ruta']}")
    print(f"      Tipo: {meta['tipo']}")
    if meta['titulo']:
        print(f"      Título: {meta['titulo']}")
    if meta['version']:
        print(f"      Versión: {meta['version']}")
    if meta['fecha']:
        print(f"      Fecha: {meta['fecha']}")
    if meta['estado']:
        print(f"      Estado: {meta['estado']}")
    print()

# Guardar reporte completo en JSON
with open("auditoria_constitucional_completa.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 80)
print("✅ AUDITORÍA COMPLETADA")
print(f"📄 Reporte completo guardado en: auditoria_constitucional_completa.json")
print("=" * 80)
EOF

python3 << 'EOF'
import subprocess
import json

print("=" * 80)
print("🔍 VERIFICACIÓN DE ESTADO DE RAMAS")
print("=" * 80)

# 1. Ver rama actual local
print("\n📍 RAMA ACTUAL EN TERMUX:")
result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
rama_actual = result.stdout.strip()
print(f"   Rama activa: {rama_actual}")

# 2. Ver todas las ramas locales
print("\n📋 RAMAS LOCALES:")
result = subprocess.run(["git", "branch"], capture_output=True, text=True)
print(result.stdout)

# 3. Ver ramas remotas
print("\n🌐 RAMAS REMOTAS (GitHub):")
result = subprocess.run(["git", "branch", "-r"], capture_output=True, text=True)
print(result.stdout)

# 4. Ver último commit de cada rama
print("\n📊 ÚLTIMOS COMMITS:")
result = subprocess.run(["git", "log", "--oneline", "--all", "--graph", "-10"], capture_output=True, text=True)
print(result.stdout)

# 5. Ver archivos en rama main (si existe)
print("\n📁 ARCHIVOS EN RAMA MAIN (GitHub):")
result = subprocess.run(["git", "ls-tree", "-r", "origin/main", "--name-only"], capture_output=True, text=True)
if result.returncode == 0:
    archivos_main = result.stdout.strip().split('\n')
    print(f"   Total de archivos en main: {len(archivos_main)}")
    
    # Filtrar archivos relacionados con constitución
    const_files = [f for f in archivos_main if any(palabra in f.lower() for palabra in ['constitucion', 'ley-', 'norma-', 'acta', 'biblia', 'manifest'])]
    print(f"   Archivos de constitución/leyes en main: {len(const_files)}")
    
    print("\n   Primeros 20 archivos de constitución en main:")
    for f in const_files[:20]:
        print(f"      - {f}")
else:
    print("   ⚠️ No se pudo acceder a origin/main")

# 6. Ver archivos en rama soberano-v1
print("\n📁 ARCHIVOS EN RAMA SOBERANO-V1:")
result = subprocess.run(["git", "ls-tree", "-r", "origin/soberano-v1", "--name-only"], capture_output=True, text=True)
if result.returncode == 0:
    archivos_soberano = result.stdout.strip().split('\n')
    print(f"   Total de archivos en soberano-v1: {len(archivos_soberano)}")
    
    const_files_sv = [f for f in archivos_soberano if any(palabra in f.lower() for palabra in ['constitucion', 'ley-', 'norma-', 'acta', 'biblia', 'manifest'])]
    print(f"   Archivos de constitución/leyes en soberano-v1: {len(const_files_sv)}")
else:
    print("   ⚠️ No se pudo acceder a origin/soberano-v1")

print("\n" + "=" * 80)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 80)
EOF

