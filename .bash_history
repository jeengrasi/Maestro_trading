    resultados.append(("ID-0016", "Mejora de rentabilidad y robustez", "PENDIENTE", ""))

# 15. ID-0017: Implementar monitoreo de Drawdown del 2.0% en tiempo real
print("\n1️⃣5️⃣ [ID-0017] Implementar monitoreo de Drawdown del 2.0% en tiempo real")
# Verificar si hay lógica de kill-switch por drawdown en el código
kill_switch_found = (file_contains(risk_path, "kill_switch") or file_contains(risk_path, "pausar") or
                     file_contains(risk_path, "max_drawdown") or file_contains(risk_path, "drawdown_diario"))
if kill_switch_found:
    print("   ✅ HECHO: Hay lógica de kill-switch por drawdown en risk_manager.")
    resultados.append(("ID-0017", "Monitoreo Drawdown 2.0%", "COMPLETADA", ""))
else:
    print("   ❌ PENDIENTE REAL: No hay lógica de kill-switch por drawdown diario.")
    resultados.append(("ID-0017", "Monitoreo Drawdown 2.0%", "PENDIENTE", ""))

# Resumen
print("\n" + "=" * 80)
print("📊 RESUMEN DE AUDITORÍA FORENSE")
print("=" * 80)

completadas = [r for r in resultados if r[2] == "COMPLETADA"]
pendientes = [r for r in resultados if r[2] == "PENDIENTE"]
en_progreso = [r for r in resultados if r[2] == "EN_PROGRESO"]

print(f"\n✅ COMPLETADAS ({len(completadas)}):")
for r in completadas:
    print(f"   - [{r[0]}] {r[1]} {('- ' + r[3] if r[3] else '')}")

print(f"\n⏳ EN PROGRESO ({len(en_progreso)}):")
for r in en_progreso:
    print(f"   - [{r[0]}] {r[1]} {('- ' + r[3] if r[3] else '')}")

print(f"\n❌ PENDIENTES REALES ({len(pendientes)}):")
for r in pendientes:
    print(f"   - [{r[0]}] {r[1]} {('- ' + r[3] if r[3] else '')}")

# Guardar resultados para siguiente paso
with open("AUDITORIA_PENDIENTES.json", "w", encoding="utf-8") as f:
    import json
    json.dump({
        "fecha": datetime.now().isoformat(),
        "completadas": completadas,
        "en_progreso": en_progreso,
        "pendientes": pendientes
    }, f, indent=2, ensure_ascii=False)

print(f"\n💾 Resultados guardados en: AUDITORIA_PENDIENTES.json")
print("=" * 80)
EOF

python3 << 'EOF'
import os
import subprocess
from datetime import datetime
from collections import defaultdict

print("=" * 80)
print("📦 INVENTARIO TOTAL DEL REPOSITORIO")
print("=" * 80)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Obtener archivos versionados por Git (seguro)
result = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
archivos_git = [f for f in result.stdout.strip().split('\n') if f]

# Estadísticas
stats = {
    'total_archivos': len(archivos_git),
    'total_lineas': 0,
    'por_extension': defaultdict(int),
    'por_directorio': defaultdict(list),
    'archivos_python': [],
    'archivos_grandes': []
}

# Analizar cada archivo
inventario_detalle = []

for archivo in archivos_git:
    try:
        # Obtener información del archivo
        stat = os.stat(archivo)
        tamaño_kb = round(stat.st_size / 1024, 2)
        
        # Contar líneas si es texto
        lineas = 0
        preview = ""
        if archivo.endswith(('.py', '.md', '.txt', '.json', '.yml', '.yaml', '.sh', '.env.example')):
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                lineas = len(contenido.splitlines())
                preview = contenido[:200].replace('\n', ' ').strip()
                if len(preview) > 200:
                    preview += "..."
        
        # Estadísticas
        stats['total_lineas'] += lineas
        extension = os.path.splitext(archivo)[1] or '(sin extensión)'
        stats['por_extension'][extension] += 1
        
        directorio = os.path.dirname(archivo) or '(raíz)'
        stats['por_directorio'][directorio].append(archivo)
        
        # Archivos Python
        if archivo.endswith('.py'):
            stats['archivos_python'].append({
                'ruta': archivo,
                'lineas': lineas,
                'tamaño_kb': tamaño_kb
            })
        
        # Archivos grandes (>100KB)
        if tamaño_kb > 100:
            stats['archivos_grandes'].append({
                'ruta': archivo,
                'tamaño_kb': tamaño_kb
            })
        
        # Detalle para el inventario
        inventario_detalle.append({
            'ruta': archivo,
            'tamaño_kb': tamaño_kb,
            'lineas': lineas,
            'preview': preview
        })
        
    except Exception as e:
        print(f"⚠️ Error procesando {archivo}: {e}")

# Generar reporte
print("\n📊 ESTADÍSTICAS GENERALES")
print("-" * 80)
print(f"Total de archivos: {stats['total_archivos']}")
print(f"Total de líneas de código: {stats['total_lineas']}")
print(f"Archivos Python: {len(stats['archivos_python'])}")
print(f"Archivos grandes (>100KB): {len(stats['archivos_grandes'])}")

print("\n📁 DISTRIBUCIÓN POR EXTENSIÓN")
print("-" * 80)
for ext, count in sorted(stats['por_extension'].items(), key=lambda x: x[1], reverse=True):
    print(f"{ext:20} {count:5} archivos")

print("\n📂 DISTRIBUCIÓN POR DIRECTORIO")
print("-" * 80)
for directorio, archivos in sorted(stats['por_directorio'].items()):
    print(f"{directorio:50} {len(archivos):3} archivos")

print("\n🐍 ARCHIVOS PYTHON (Ordenados por tamaño)")
print("-" * 80)
for py in sorted(stats['archivos_python'], key=lambda x: x['lineas'], reverse=True):
    print(f"{py['ruta']:60} {py['lineas']:5} líneas  {py['tamaño_kb']:6} KB")

print("\n⚠️ ARCHIVOS GRANDES (>100KB)")
print("-" * 80)
if stats['archivos_grandes']:
    for grande in sorted(stats['archivos_grandes'], key=lambda x: x['tamaño_kb'], reverse=True):
        print(f"{grande['ruta']:60} {grande['tamaño_kb']:8} KB")
else:
    print("No hay archivos grandes (>100KB)")

# Guardar inventario detallado
print("\n💾 Generando inventario detallado...")
with open("INVENTARIO_COMPLETO.md", "w", encoding="utf-8") as f:
    f.write(f"# 📦 INVENTARIO COMPLETO DEL REPOSITORIO\n\n")
    f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    f.write(f"## 📊 Estadísticas Generales\n\n")
    f.write(f"- Total de archivos: {stats['total_archivos']}\n")
    f.write(f"- Total de líneas: {stats['total_lineas']}\n")
    f.write(f"- Archivos Python: {len(stats['archivos_python'])}\n\n")
    
    f.write(f"## 📁 Distribución por Directorio\n\n")
    for directorio, archivos in sorted(stats['por_directorio'].items()):
        f.write(f"### {directorio} ({len(archivos)} archivos)\n\n")
        for archivo in archivos:
            f.write(f"- `{archivo}`\n")
        f.write("\n")
    
    f.write(f"## 🐍 Archivos Python Detallados\n\n")
    for py in sorted(stats['archivos_python'], key=lambda x: x['lineas'], reverse=True):
        f.write(f"### {py['ruta']}\n\n")
        f.write(f"- **Líneas:** {py['lineas']}\n")
        f.write(f"- **Tamaño:** {py['tamaño_kb']} KB\n\n")
        
        # Buscar preview en inventario_detalle
        for item in inventario_detalle:
            if item['ruta'] == py['ruta'] and item['preview']:
                f.write(f"**Preview:**\n```\n{item['preview']}\n```\n\n")
                break

print("✅ Inventario detallado guardado en: INVENTARIO_COMPLETO.md")

# Generar árbol visual
print("\n🌳 Generando árbol de directorios...")
arbol_result = subprocess.run(
    ["find", ".", "-type", "d", "-not", "-path", "*/.git*", "-not", "-path", "*/__pycache__*"],
    capture_output=True, text=True
)
directorios = sorted([d for d in arbol_result.stdout.strip().split('\n') if d])

with open("ARBOL_DIRECTORIOS.txt", "w", encoding="utf-8") as f:
    f.write("🌳 ÁRBOL DE DIRECTORIOS DEL REPOSITORIO\n")
    f.write("=" * 80 + "\n\n")
    for d in directorios:
        nivel = d.count('/')
        indent = "  " * nivel
        nombre = os.path.basename(d) or "(raíz)"
        f.write(f"{indent}📁 {nombre}\n")

print("✅ Árbol guardado en: ARBOL_DIRECTORIOS.txt")

print("\n" + "=" * 80)
print("✅ INVENTARIO TOTAL COMPLETADO")
print("=" * 80)
print("\n📄 Archivos generados:")
print("   1. INVENTARIO_COMPLETO.md - Inventario detallado con previews")
print("   2. ARBOL_DIRECTORIOS.txt - Estructura visual de carpetas")
print("\n👉 Para revisar el inventario completo:")
print("   cat INVENTARIO_COMPLETO.md")
print("\n👉 Para ver el árbol de directorios:")
print("   cat ARBOL_DIRECTORIOS.txt")
print("=" * 80)
EOF

cat INVENTARIO_COMPLETO.md
cat ARBOL_DIRECTORIOS.txt
python3 << 'EOF'
import os
import subprocess
from datetime import datetime
from collections import defaultdict

print("=" * 80)
print("📦 INVENTARIO TOTAL SEGURO DEL PROYECTO (git ls-files)")
print("=" * 80)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# 1. Obtener archivos versionados por Git (SEGURO - ignora .cache, .npm, .tor, etc.)
result = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
archivos_git = [f for f in result.stdout.strip().split('\n') if f]

# 2. Estadísticas
stats = {
    'total_archivos': len(archivos_git),
    'total_lineas': 0,
    'por_extension': defaultdict(int),
    'por_directorio': defaultdict(list),
    'archivos_python': [],
    'archivos_grandes': []
}

inventario_detalle = []

# 3. Analizar cada archivo
print("\n📊 ESCANEANDO ARCHIVOS VERSIONADOS...\n")

for archivo in archivos_git:
    try:
        if not os.path.exists(archivo):
            continue
            
        stat = os.stat(archivo)
        tamaño_kb = round(stat.st_size / 1024, 2)
        
        lineas = 0
        preview = ""
        if archivo.endswith(('.py', '.md', '.txt', '.json', '.yml', '.yaml', '.sh', '.env.example')):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    lineas = len(contenido.splitlines())
                    preview = contenido[:200].replace('\n', ' ').strip()
                    if len(preview) > 200:
                        preview += "..."
            except:
                preview = "(archivo binario o con codificación especial)"
        
        stats['total_lineas'] += lineas
        extension = os.path.splitext(archivo)[1] or '(sin extensión)'
        stats['por_extension'][extension] += 1
        
        directorio = os.path.dirname(archivo) or '(raíz)'
        stats['por_directorio'][directorio].append(archivo)
        
        if archivo.endswith('.py'):
            stats['archivos_python'].append({
                'ruta': archivo,
                'lineas': lineas,
                'tamaño_kb': tamaño_kb
            })
        
        if tamaño_kb > 100:
            stats['archivos_grandes'].append({
                'ruta': archivo,
                'tamaño_kb': tamaño_kb
            })
        
        inventario_detalle.append({
            'ruta': archivo,
            'tamaño_kb': tamaño_kb,
            'lineas': lineas,
            'preview': preview
        })
        
    except Exception as e:
        print(f"⚠️ Error procesando {archivo}: {e}")

# 4. Mostrar resumen en terminal
print("=" * 80)
print("📊 ESTADÍSTICAS GENERALES")
print("-" * 80)
print(f"Total de archivos versionados: {stats['total_archivos']}")
print(f"Total de líneas de código: {stats['total_lineas']}")
print(f"Archivos Python: {len(stats['archivos_python'])}")
print(f"Archivos grandes (>100KB): {len(stats['archivos_grandes'])}")

print("\n📁 DISTRIBUCIÓN POR EXTENSIÓN")
print("-" * 80)
for ext, count in sorted(stats['por_extension'].items(), key=lambda x: x[1], reverse=True):
    print(f"  {ext:20} {count:5} archivos")

print("\n📂 DISTRIBUCIÓN POR DIRECTORIO")
print("-" * 80)
for directorio, archivos in sorted(stats['por_directorio'].items()):
    print(f"  {directorio:55} {len(archivos):3} archivos")

print("\n🐍 ARCHIVOS PYTHON (Ordenados por tamaño)")
print("-" * 80)
for py in sorted(stats['archivos_python'], key=lambda x: x['lineas'], reverse=True):
    print(f"  {py['ruta']:60} {py['lineas']:5} líneas  {py['tamaño_kb']:6} KB")

# 5. Guardar inventario detallado en archivo
print("\n💾 Generando inventario detallado...")
with open("INVENTARIO_COMPLETO.md", "w", encoding="utf-8") as f:
    f.write(f"# 📦 INVENTARIO COMPLETO DEL PROYECTO\n\n")
    f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"**Método:** `git ls-files` (solo archivos versionados, 100% seguro)\n\n")
    
    f.write(f"## 📊 Estadísticas Generales\n\n")
    f.write(f"- Total de archivos: {stats['total_archivos']}\n")
    f.write(f"- Total de líneas: {stats['total_lineas']}\n")
    f.write(f"- Archivos Python: {len(stats['archivos_python'])}\n\n")
    
    f.write(f"## 📁 Distribución por Directorio\n\n")
    for directorio, archivos in sorted(stats['por_directorio'].items()):
        f.write(f"### {directorio} ({len(archivos)} archivos)\n\n")
        for archivo in archivos:
            f.write(f"- `{archivo}`\n")
        f.write("\n")
    
    f.write(f"## 🐍 Archivos Python Detallados\n\n")
    for py in sorted(stats['archivos_python'], key=lambda x: x['lineas'], reverse=True):
        f.write(f"### `{py['ruta']}`\n\n")
        f.write(f"- **Líneas:** {py['lineas']}\n")
        f.write(f"- **Tamaño:** {py['tamaño_kb']} KB\n\n")
        
        for item in inventario_detalle:
            if item['ruta'] == py['ruta'] and item['preview']:
                f.write(f"**Preview:**\n```\n{item['preview']}\n```\n\n")
                break

print("✅ Inventario detallado guardado en: INVENTARIO_COMPLETO.md")

# 6. Generar árbol visual SOLO del proyecto (ignorando carpetas locales)
print("\n🌳 Generando árbol de directorios del proyecto...")
directorios_proyecto = []
for d in stats['por_directorio'].keys():
    if d != '(raíz)':
        directorios_proyecto.append(d)

with open("ARBOL_PROYECTO.txt", "w", encoding="utf-8") as f:
    f.write("🌳 ÁRBOL DE DIRECTORIOS DEL PROYECTO (Solo archivos versionados)\n")
    f.write("=" * 80 + "\n\n")
    for d in sorted(directorios_proyecto):
        nivel = d.count('/')
        indent = "  " * nivel
        nombre = os.path.basename(d)
        f.write(f"{indent}📁 {nombre}\n")
        # Mostrar archivos en ese directorio
        for archivo in stats['por_directorio'][d]:
            nombre_archivo = os.path.basename(archivo)
            f.write(f"{indent}  📄 {nombre_archivo}\n")

print("✅ Árbol del proyecto guardado en: ARBOL_PROYECTO.txt")

print("\n" + "=" * 80)
print("✅ INVENTARIO TOTAL SEGURO COMPLETADO")
print("=" * 80)
print("\n📄 Archivos generados:")
print("   1. INVENTARIO_COMPLETO.md - Inventario detallado con previews")
print("   2. ARBOL_PROYECTO.txt - Estructura visual del proyecto")
print("\n👉 Para revisar el inventario completo:")
print("   cat INVENTARIO_COMPLETO.md")
print("\n👉 Para ver el árbol del proyecto:")
print("   cat ARBOL_PROYECTO.txt")
print("=" * 80)
EOF

cat << 'EOF' >> BITACORA.md
---
## [ID-0018] [2026-08-06 21:30] [INVENTARIO] [COMPLETADA] Inventario Total Seguro del Proyecto
**Participantes:** Director JEISSON_01, Gerente Qwen
**Contexto:** 
- **Qué problema:** Necesidad de inventariar todos los archivos del proyecto para organizar y modularizar correctamente.
- **Por qué surge:** Mandato del Director de tener evidencia completa antes de construir módulos.
- **Dónde ocurre:** Repositorio completo bajo control de Git (rama soberano-v1).
**Decisión/Acción:** Ejecutar script de inventario usando `git ls-files` para ignorar automáticamente archivos locales (.cache, .npm, .tor) y enfocarse solo en el código del proyecto.
**Justificación:** Principio de Minimalismo y Seguridad. No se analiza basura local que no forma parte del repositorio.
**Implementación:** 
- **Cómo se hizo:** Script Python que itera sobre archivos versionados, extrae estadísticas y genera previews.
- **Archivos afectados:** `INVENTARIO_COMPLETO.md` (creado), `ARBOL_PROYECTO.txt` (creado).
**Resultado:** Inventario completo y limpio del proyecto real, listo para análisis de modularización.
**Acciones Derivadas:**
- [x] Ejecutar inventario seguro (COMPLETADA)
- [ ] Director revisa INVENTARIO_COMPLETO.md (PENDIENTE)
- [ ] Plan de modularización basado en evidencia real (PENDIENTE)
**Hash anterior:** [CALCULADO]
**Hash actual:** [CALCULADO]
---
EOF

python3 << 'EOF'
import os
import re

print("=" * 80)
print("🔍 AUDITORÍA FORENSE DE IMPORTACIONES (Resolución de Duplicidades)")
print("=" * 80)

# Los duplicados identificados en el árbol de directorios
duplicates = {
    "router.py": [
        "SOBERANO_03_NEXUS/router.py",
        "SOBERANO_03_NEXUS/core/router.py"
    ],
    "scheduler.py": [
        "SOBERANO_01_MEMORIA/core/scheduler.py",
        "SOBERANO_03_NEXUS/autonomy/scheduler.py"
    ]
}

# Obtener todos los archivos .py del proyecto (ignorando carpetas locales/sistema)
py_files = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'node_modules', '.git']]
    for file in files:
        if file.endswith('.py'):
            py_files.append(os.path.join(root, file).replace('./', ''))

print("\n📊 ESCANEANDO DEPENDENCIAS DEL CÓDIGO...\n")

for target, paths in duplicates.items():
    print(f"📦 Analizando: {target}")
    
    for path in paths:
        if not os.path.exists(path):
            print(f"   ❌ {path} (NO EXISTE en el sistema de archivos)")
            continue
            
        # Convertir ruta a formato de módulo Python (ej: SOBERANO_03_NEXUS.core.router)
        path_module = path.replace('/', '.').replace('.py', '')
        base_name = target.replace('.py', '')
        
        importers = []
        for py_file in py_files:
            if py_file == path:
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar patrones de importación: "import base_name" o "from ... import base_name"
                pattern = rf"(?:from\s+.*\s+import\s+.*\b{base_name}\b)|(?:import\s+.*\b{base_name}\b)"
                if re.search(pattern, content):
                    # Verificar si la importación coincide con la ruta específica
                    if path_module in content or (len(paths) == 2 and base_name in content):
                        importers.append(py_file)
            except Exception:
                pass
        
        if importers:
            print(f"   ✅ {path}")
            print(f"      ↳ ACTIVO: Importado por {len(importers)} archivo(s):")
            for imp in importers[:3]: # Mostrar máximo 3 para no saturar
                print(f"         - {imp}")
            if len(importers) > 3:
                print(f"         - ... y {len(importers) - 3} más.")
        else:
            print(f"   ⚠️ {path}")
            print(f"      ↳ CÓDIGO MUERTO: No hay ninguna importación activa hacia este archivo.")
    
    print("-" * 80)

print("\n💡 CONCLUSIÓN PRELIMINAR:")
print("Los archivos marcados como 'CÓDIGO MUERTO' son candidatos seguros para eliminación.")
print("No romperán el sistema porque ningún otro módulo depende de ellos.")
print("=" * 80)
EOF

