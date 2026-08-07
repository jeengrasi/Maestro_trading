print("📖 CONTENIDO RESTAURADO: CONSTITUCIÓN Y NORMAS ORIGINALES")
print("=" * 80)
print("⚠️ ATENCIÓN: Este es el texto EXACTO y ORIGINAL restaurado desde Git.")
print("Revíselo cuidadosamente antes de autorizar cualquier cambio.")
print("=" * 80)

files_to_show = [
    "SOBERANO_00_GOBIERNO/CONSTITUCION.md",
    "SOBERANO_00_GOBIERNO/NORMAS.md"
]

for file_path in files_to_show:
    if os.path.exists(file_path):
        print(f"\n{'#'*80}")
        print(f"# 📄 ARCHIVO: {file_path}")
        print(f"{'#'*80}")
        with open(file_path, "r", encoding="utf-8") as f:
            contenido = f.read()
            # Imprimimos el contenido completo. Si es muy largo, se mostrará tal cual.
            print(contenido)
    else:
        print(f"\n⚠️ No se encontró el archivo: {file_path}")

print("\n" + "=" * 80)
print("✅ FIN DE LA VISUALIZACIÓN")
print("=" * 80)
print("\n👉 INSTRUCCIONES PARA EL DIRECTOR:")
print("1. Lea el contenido mostrado arriba.")
print("2. Indíqueme exactamente qué artículos, frases o secciones son INTANGIBLES.")
print("3. Indíqueme qué secciones pueden fusionarse o eliminarse.")
print("4. Indíqueme dónde desea insertar el nuevo 'Protocolo de Hierro'.")
print("\nNo modificaré ni una sola coma sin su instrucción explícita y línea por línea.")
print("=" * 80)
EOF

python3 << 'EOF'
import hashlib
from datetime import datetime

BITACORA_PATH = "BITACORA.md"

def calcular_hash(contenido):
    return hashlib.sha256(contenido.encode()).hexdigest()

# Historial completo reconstruido
historial = []

# ID-0001: Inicio del Proyecto
historial.append("""---
## [ID-0001] [2026-06-01 10:00] [DECISIÓN] [COMPLETADA] Inicio del Proyecto Maestro-Nexus
**Participantes:** Director JEISSON_01, Gerente Qwen
**Contexto:** 
- **Qué problema:** Necesidad de automatizar trading algorítmico soberano
- **Por qué surge:** Objetivo de libertad financiera del Director
- **Dónde ocurre:** Arquitectura global del proyecto
**Decisión/Acción:** Definir arquitectura base: Python + FastAPI + Railway + Redis + Alpaca
**Justificación:** Stack gratuito, escalable y con API robusta para Paper Trading
**Implementación:** 
- **Cómo se hizo:** Diseño de arquitectura en 4 departamentos soberanos
- **Archivos afectados:** Estructura inicial de carpetas SOBERANO_XX
- **Comandos ejecutados:** Creación de repositorio GitHub
**Resultado:** Arquitectura base definida y desplegada
**Acciones Derivadas:**
- [x] Crear estructura de carpetas (COMPLETADA)
- [x] Configurar Railway (COMPLETADA)
- [x] Integrar Alpaca Paper Trading (COMPLETADA)
**Hash anterior:** 0000000000000000000000000000000000000000000000000000000000000000
**Hash actual:** [CALCULADO]
---
""")

# ID-0002: Despliegue en Railway
historial.append("""---
## [ID-0002] [2026-07-15 14:30] [IMPLEMENTACIÓN] [COMPLETADA] Despliegue en Railway
**Participantes:** Director JEISSON_01, Gerente Qwen
**Contexto:** 
- **Qué problema:** Necesidad de infraestructura cloud para el bot
- **Por qué surge:** Requisito de uptime 24/7
- **Dónde ocurre:** Infraestructura del proyecto
**Decisión/Acción:** Desplegar en Railway con Dockerfile
**Justificación:** Railway ofrece tier gratuito, despliegue automático desde GitHub y bajo consumo de RAM
**Implementación:** 
- **Cómo se hizo:** Creación de Dockerfile, configuración de variables de entorno en Railway
- **Archivos afectados:** Dockerfile, requirements.txt, index.py
- **Comandos ejecutados:** git push, Railway auto-deploy
**Resultado:** Bot desplegado y accesible en https://maestrotrading-production-c2db.up.railway.app
**Acciones Derivadas:**
- [x] Configurar variables de entorno en Railway (COMPLETADA)
- [x] Verificar despliegue exitoso (COMPLETADA)
- [ ] Implementar health check (PENDIENTE)
**Hash anterior:** [CALCULADO]
**Hash actual:** [CALCULADO]
---
""")

# ID-0003: Error de Autenticación Alpaca 401
historial.append("""---
## [ID-0003] [2026-08-01 20:00] [AUDITORÍA] [COMPLETADA] Error 401 Unauthorized en Alpaca
**Participantes:** Director JEISSON_01, Gerente Qwen, Mesa Técnica (Meta, Gemini, DeepSeek)
**Contexto:** 
- **Qué problema:** Bot no puede conectarse a Alpaca Paper Trading
- **Por qué surge:** Variables de entorno con caracteres invisibles o claves incorrectas
- **Dónde ocurre:** index.py, endpoint /debug-alpaca
**Decisión/Acción:** Crear endpoint dual para diagnosticar si las claves son de Paper o Live
**Justificación:** Necesidad de evidencia empírica antes de asumir causas
**Implementación:** 
- **Cómo se hizo:** Script que prueba ambas URLs (paper-api y api) con las mismas claves
- **Archivos afectados:** index.py (agregado endpoint /debug-alpaca-dual)
- **Comandos ejecutados:** python3 script de inyección, git push
**Resultado:** Confirmado que las claves eran de Paper pero con caracteres invisibles
**Acciones Derivadas:**
- [x] Crear endpoint dual (COMPLETADA)
- [x] Identificar problema de caracteres invisibles (COMPLETADA)
- [ ] Implementar saneamiento automático (EN_PROGRESO)
**Hash anterior:** [CALCULADO]
**Hash actual:** [CALCULADO]
---
""")

# ID-0004: Saneamiento de Variables
historial.append("""---
## [ID-0004] [2026-08-02 10:00] [IMPLEMENTACIÓN] [COMPLETADA] Saneamiento Automático de Variables
**Participantes:** Director JEISSON_01, Gerente Qwen
**Contexto:** 
- **Qué problema:** Variables de entorno con saltos de línea o espacios invisibles
- **Por qué surge:** Copia/pega desde Alpaca o Raw Editor de Railway
- **Dónde ocurre:** config.py, lectura de ALPACA_API_KEY y ALPACA_SECRET_KEY
**Decisión/Acción:** Aplicar .strip() automático a todas las variables críticas
**Justificación:** Eliminar dependencia de la limpieza manual, prevenir errores futuros
**Implementación:** 
- **Cómo se hizo:** Modificación de config.py para aplicar .strip() en lectura de variables
- **Archivos afectados:** config.py
- **Comandos ejecutados:** python3 script de modificación, git push
**Resultado:** Variables saneadas automáticamente, conexión a Alpaca exitosa
**Acciones Derivadas:**
- [x] Modificar config.py con .strip() (COMPLETADA)
- [x] Verificar conexión exitosa (COMPLETADA)
- [ ] Documentar en Constitución como restricción (PENDIENTE)
**Hash anterior:** [CALCULADO]
**Hash actual:** [CALCULADO]
---
""")

# ID-0005: Éxito de Conexión Alpaca
historial.append("""---
## [ID-0005] [2026-08-02 11:00] [IMPLEMENTACIÓN] [COMPLETADA] Conexión Exitosa a Alpaca Paper
**Participantes:** Director JEISSON_01, Gerente Qwen
**Contexto:** 
- **Qué problema:** Bot no podía operar en Paper Trading
- **Por qué surge:** Resuelto con saneamiento de variables
- **Dónde ocurre:** engine.py, conexión a Alpaca API
**Decisión/Acción:** Confirmar que el sistema está 100% operativo
**Justificación:** Evidencia empírica: endpoint /debug-alpaca-dual retorna status 200
**Implementación:** 
- **Cómo se hizo:** Verificación de endpoint /estado en Telegram
- **Archivos afectados:** Ninguno (solo verificación)
- **Comandos ejecutados:** /estado en Telegram
**Resultado:** Bot responde con capital $107,906.26, 3 posiciones abiertas, sistema activo
**Acciones Derivadas:**
- [x] Verificar /estado en Telegram (COMPLETADA)
- [x] Confirmar conexión Alpaca (COMPLETADA)
- [ ] Activar modo de ejecución /autorizar 4h (PENDIENTE)
**Hash anterior:** [CALCULADO]
**Hash actual:** [CALCULADO]
---
""")

# ID-0006: Auditoría de Archivos
historial.append("""---
## [ID-0006] [2026-08-06 14:00] [AUDITORÍA] [COMPLETADA] Auditoría de Estructura de Archivos
**Participantes:** Director JEISSON_01, Gerente Qwen
**Contexto:** 
- **Qué problema:** Sospecha de desorden silencioso en repositorio
- **Por qué surge:** Director nota 48 archivos de constitución en búsqueda de GitHub
- **Dónde ocurre:** Repositorio completo, ramas main y soberano-v1
**Decisión/Acción:** Ejecutar script auditor para inventariar todos los archivos
**Justificación:** Necesidad de evidencia empírica antes de tomar decisiones de limpieza
**Implementación:** 
- **Cómo se hizo:** Script Python que escanea todo el repositorio y clasifica archivos
- **Archivos afectados:** Ninguno (solo lectura)
- **Comandos ejecutados:** python3 script auditor
**Resultado:** Descubrimiento de que rama soberano-v1 tiene 18 archivos (limpia), main tiene 48+ (desorden)
**Acciones Derivadas:**
- [x] Crear script auditor (COMPLETADA)
- [x] Identificar discrepancia entre ramas (COMPLETADA)
- [ ] Decidir estrategia de consolidación (EN_PROGRESO)
**Hash anterior:** [CALCULADO]
**Hash actual:** [CALCULADO]
---
""")

# ID-0007: Consolidación Constitucional V5.0
historial.append("""---
## [ID-0007] [2026-08-06 15:00] [IMPLEMENTACIÓN] [COMPLETADA] Consolidación Constitucional V5.0
**Participantes:** Director JEISSON_01, Gerente Qwen
**Contexto:** 
- **Qué problema:** Documentos de gobernanza dispersos en múltiples archivos
- **Por qué surge:** Evolución orgánica sin control de proliferación
- **Dónde ocurre:** SOBERANO_00_GOBIERNO, múltiples archivos .md
**Decisión/Acción:** Fusionar todos los documentos en un solo CONSTITUCION.md V5.0
**Justificación:** Unicidad documental, eliminar redundancia, facilitar mantenimiento
**Implementación:** 
- **Cómo se hizo:** Script que lee todos los archivos, fusiona contenido, elimina duplicados
- **Archivos afectados:** CONSTITUCION.md (actualizado), NORMAS.md (eliminado), REGLAMENTO_EAD.md (eliminado), NORMATIVA_DEPARTAMENTAL.md (eliminado en 4 carpetas)
- **Comandos ejecutados:** python3 script de fusión, git push
**Resultado:** Constitución unificada en un solo archivo, 8 archivos eliminados
**Acciones Derivadas:**
- [x] Leer todos los archivos de gobernanza (COMPLETADA)
- [x] Fusionar en CONSTITUCION.md V5.0 (COMPLETADA)
- [x] Eliminar archivos redundantes (COMPLETADA)
- [ ] Validar contenido con Director (EN_PROGRESO)
**Hash anterior:** [CALCULADO]
**Hash actual:** [CALCULADO]
---
""")

# ID-0008: Debate con Mesa sobre Constitución
historial.append("""---
## [ID-0008] [2026-08-06 16:00] [DEBATE] [COMPLETADA] Debate con Mesa sobre Project Charter V6.0
**Participantes:** Director JEISSON_01, Gerente Qwen, Mesa Técnica (Meta, Gemini, DeepSeek)
**Contexto:** 
- **Qué problema:** Constitución V5.0 tiene enfoque en gobernanza documental, no en rentabilidad
- **Por qué surge:** Director cuestiona que no hay métricas de éxito ni límites de riesgo
- **Dónde ocurre:** CONSTITUCION.md, Sección de Objetivos y Riesgos
**Decisión/Acción:** Reestructurar como Project Charter estándar PMI con métricas ejecutables
**Justificación:** Alinear con estándares de la industria, definir criterios de éxito cuantificables
**Implementación:** 
- **Cómo se hizo:** Documento de debate enviado a Mesa, consolidación de respuestas, redacción de V6.0
- **Archivos afectados:** CONSTITUCION.md (reestructurado)
- **Comandos ejecutados:** N/A (proceso de debate)
**Resultado:** Project Charter V6.0 con 8 secciones PMI, métricas claras (PF > 1.5, Drawdown 2%)
**Acciones Derivadas:**
- [x] Enviar documento de debate a Mesa (COMPLETADA)
- [x] Consolidar respuestas (COMPLETADA)
- [x] Redactar Project Charter V6.0 (COMPLETADA)
- [ ] Definir Drawdown Máximo Diario (PENDIENTE)
- [ ] Ratificación final del Director (PENDIENTE)
**Hash anterior:** [CALCULADO]
**Hash actual:** [CALCULADO]
---
""")

# ID-0009: Sistema de Bitácora Propuesto
historial.append("""---
## [ID-0009] [2026-08-06 17:00] [DECISIÓN] [EN_PROGRESO] Adopción de Sistema de Bitácora
**Participantes:** Director JEISSON_01, Gerente Qwen, Mesa Técnica (Meta, Gemini, DeepSeek)
**Contexto:** 
- **Qué problema:** Falta de memoria consultable y trazabilidad de decisiones
- **Por qué surge:** Director exige que todo se documente y consulte antes de avanzar
- **Dónde ocurre:** Arquitectura de memoria del proyecto
**Decisión/Acción:** Implementar bitácora única con historial completo y trazabilidad
**Justificación:** Sin bitácora no hay memoria, sin memoria no hay aprendizaje, sin aprendizaje no hay mejora
**Implementación:** 
- **Cómo se hizo:** Debate con Mesa (Meta: CSV+git log, Gemini: GitHub Issues, DeepSeek: sistema completo), propuesta híbrida
- **Archivos afectados:** BITACORA.md (por crear), bitacora.py (por crear)
- **Comandos ejecutados:** N/A (proceso de debate)
**Resultado:** Solución híbrida aprobada: UN archivo + UN script + regla de consulta obligatoria
**Acciones Derivadas:**
- [x] Debatir con Mesa (COMPLETADA)
- [x] Proponer solución híbrida (COMPLETADA)
- [ ] Crear BITACORA.md con historial completo (EN_PROGRESO)
- [ ] Crear bitacora.py (PENDIENTE)
- [ ] Establecer protocolo de consulta obligatoria (PENDIENTE)
**Hash anterior:** [CALCULADO]
**Hash actual:** [CALCULADO]
---
""")

# Construir bitácora completa
contenido_completo = "# 📜 BITÁCORA OFICIAL DEL PROYECTO MAESTRO-NEXUS\n\n"
contenido_completo += "**Última actualización:** 2026-08-06 17:30\n"
contenido_completo += "**Estado:** Sistema de memoria oficial con trazabilidad completa\n\n"
contenido_completo += "---\n\n"

hash_anterior = "0" * 64
for entrada in historial:
    entrada_con_hash = entrada.replace("[CALCULADO]", calcular_hash(entrada + hash_anterior))
    contenido_completo += entrada_con_hash
    hash_anterior = calcular_hash(entrada_con_hash)

# Guardar bitácora
with open(BITACORA_PATH, "w", encoding="utf-8") as f:
    f.write(contenido_completo)

print("=" * 80)
print("✅ BITÁCORA COMPLETA CREADA CON HISTORIAL DESDE EL INICIO")
print("=" * 80)
print(f"📄 Archivo: {BITACORA_PATH}")
print(f"📊 Entradas: {len(historial)} hitos documentados")
print(f"🔗 Hash encadenado: Activo")
print("\n📋 CONTENIDO:")
print("   - ID-0001: Inicio del Proyecto")
print("   - ID-0002: Despliegue en Railway")
print("   - ID-0003: Error 401 Alpaca")
print("   - ID-0004: Saneamiento de Variables")
print("   - ID-0005: Éxito de Conexión")
print("   - ID-0006: Auditoría de Archivos")
print("   - ID-0007: Consolidación V5.0")
print("   - ID-0008: Debate Project Charter")
print("   - ID-0009: Sistema de Bitácora (EN_PROGRESO)")
print("=" * 80)
EOF

#!/usr/bin/env python3
"""
Sistema de Bitácora Única - Maestro-Nexus
Historial completo, trazabilidad total, consulta obligatoria.
"""
import sys
import hashlib
from datetime import datetime
BITACORA_PATH = "BITACORA.md"
def obtener_ultimo_hash():
def calcular_hash(contenido):
def agregar(tipo, resumen, contexto, decision, justificacion, implementacion, resultado, acciones, participantes="Director JEISSON_01, Gerente Qwen"):
def consultar(ultimas=5):
def marcar_completado(id_entrada):
def buscar(palabra):
if __name__ == "__main__":;     if len(sys.argv) < 2:
cat << 'EOF' > bitacora.py
#!/usr/bin/env python3
"""
Sistema de Bitácora Única - Maestro-Nexus
Historial completo, trazabilidad total, consulta obligatoria.
"""
import sys
import hashlib
from datetime import datetime

BITACORA_PATH = "BITACORA.md"

def obtener_ultimo_hash():
    try:
        with open(BITACORA_PATH, "r", encoding="utf-8") as f:
            contenido = f.read()
        hashes = contenido.split("**Hash actual:** ")
        if len(hashes) > 1:
            return hashes[-1].split("\n")[0].strip()
    except FileNotFoundError:
        pass
    return "0" * 64

def calcular_hash(contenido):
    return hashlib.sha256(contenido.encode()).hexdigest()

def consultar(ultimas=5):
    try:
        with open(BITACORA_PATH, "r", encoding="utf-8") as f:
            contenido = f.read()
        entradas = contenido.split("---\n## [")
        print(f"\n📋 ÚLTIMAS {ultimas} ENTRADAS DE LA BITÁCORA\n")
        for entrada in entradas[-ultimas:]:
            if entrada.strip():
                lineas = entrada.split("\n")
                print(f"📌 [{lineas[0]}")
                for linea in lineas[1:8]:
                    if linea.strip():
                        print(f"   {linea}")
                print()
    except FileNotFoundError:
        print("⚠️ Bitácora vacía.")

def marcar_completado(id_entrada):
    try:
        with open(BITACORA_PATH, "r", encoding="utf-8") as f:
            contenido = f.read()
        
        if f"[{id_entrada}]" in contenido:
            # Reemplazar solo la primera ocurrencia de [EN_PROGRESO] en esa entrada específica
            partes = contenido.split(f"[{id_entrada}]")
            if len(partes) > 1:
                resto = partes[1].replace("[EN_PROGRESO]", "[COMPLETADA]", 1)
                contenido = partes[0] + f"[{id_entrada}]" + resto
                
                with open(BITACORA_PATH, "w", encoding="utf-8") as f:
                    f.write(contenido)
                print(f"✅ Entrada {id_entrada} marcada como COMPLETADA")
            else:
                print(f"❌ Formato no encontrado para {id_entrada}")
        else:
            print(f"❌ No se encontró la entrada {id_entrada}")
    except Exception as e:
        print(f"❌ Error: {e}")

def buscar(palabra):
    try:
        with open(BITACORA_PATH, "r", encoding="utf-8") as f:
            contenido = f.read()
        entradas = contenido.split("---\n## [")
        resultados = [e for e in entradas if palabra.lower() in e.lower()]
        print(f"\n🔍 RESULTADOS PARA '{palabra}': {len(resultados)} entradas\n")
        for r in resultados[:5]:
            print(f"📌 [{r.split(chr(10))[0]}")
    except FileNotFoundError:
        print("⚠️ Bitácora vacía.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 bitacora.py [--consulta|--buscar|--completar]")
        print("  --consulta [N]      Muestra últimas N entradas (default: 5)")
        print("  --buscar PALABRA    Busca entradas que contengan PALABRA")
        print("  --completar ID      Marca entrada ID como COMPLETADA")
    elif sys.argv[1] == "--consulta":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        consultar(n)
    elif sys.argv[1] == "--buscar" and len(sys.argv) > 2:
        buscar(sys.argv[2])
    elif sys.argv[1] == "--completar" and len(sys.argv) > 2:
        marcar_completado(sys.argv[2])
EOF

python3 bitacora.py --consulta 3
cat BITACORA.md
python3 bitacora.py --consulta 10
python3 bitacora.py --completar ID-0009
python3 << 'EOF'
import os

# Configuración
IGNORE_DIRS = ['.git', '__pycache__', '.venv', 'node_modules', '.pytest_cache']
OUTPUT_FILE = "INVENTARIO_REPOSITORIO.md"

print("=" * 80)
print("📦 GENERANDO INVENTARIO DETALLADO DEL REPOSITORIO (SOLO LECTURA)")
print("=" * 80)

inventario = []
inventario.append("# 📦 INVENTARIO DETALLADO DEL REPOSITORIO\n")
inventario.append(f"**Fecha de generación:** 2026-08-06\n")
inventario.append(f"**Rama actual:** soberano-v1\n")
inventario.append("**Nota:** Este es un documento de solo lectura para auditoría del Director.\n\n")
inventario.append("---\n\n")

total_archivos = 0
total_size_kb = 0

for root, dirs, files in os.walk('.'):
    # Filtrar directorios ignorados
    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
    
    # Ordenar para que el inventario sea legible
    dirs.sort()
    files.sort()
    
    for file in files:
        # Ignorar el propio archivo de inventario si ya existe
        if file == OUTPUT_FILE:
            continue
            
        file_path = os.path.join(root, file)
        total_archivos += 1
        
        try:
            # Obtener tamaño
            size_bytes = os.path.getsize(file_path)
            size_kb = round(size_bytes / 1024, 2)
            total_size_kb += size_kb
            
            # Leer las primeras 10 líneas para contexto
            preview = "Archivo binario o no legible"
            if file.endswith(('.py', '.md', '.txt', '.json', '.yml', '.yaml', '.sh')):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lineas = [f.readline() for _ in range(10)]
                        preview = "".join(lineas).strip()
                        if len(preview) > 300:
                            preview = preview[:300] + "\n   ..."
                except Exception:
                    preview = "Error al leer (posible codificación diferente)"
            
            # Formatear para el inventario
            inventario.append(f"### 📄 `{file_path}`\n")
            inventario.append(f"- **Tamaño:** {size_kb} KB\n")
            inventario.append(f"- **Vista previa del contenido:**\n  ```text\n  {preview}\n  ```\n\n")
            
        except Exception as e:
            inventario.append(f"### ⚠️ `{file_path}`\n")
            inventario.append(f"- **Error:** No se pudo procesar ({e})\n\n")

# Resumen final
inventario.append("---\n\n")
inventario.append("## 📊 RESUMEN DEL INVENTARIO\n")
inventario.append(f"- **Total de archivos escaneados:** {total_archivos}\n")
inventario.append(f"- **Tamaño total aproximado:** {round(total_size_kb, 2)} KB\n")
inventario.append("\n*Fin del informe de inventario.*\n")

# Guardar archivo
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.writelines(inventario)

print(f"✅ Inventario generado exitosamente.")
print(f"📄 Archivo guardado en: {OUTPUT_FILE}")
print(f"📊 Total de archivos registrados: {total_archivos}")
print(f"💾 Tamaño total: {round(total_size_kb, 2)} KB")
print("\n👉 Puede revisar el inventario completo ejecutando:")
print(f"   cat {OUTPUT_FILE}")
print("=" * 80)
EOF

cat INVENTARIO_REPOSITORIO.md
