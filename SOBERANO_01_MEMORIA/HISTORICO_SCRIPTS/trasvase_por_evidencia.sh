#!/data/data/com.termux/files/usr/bin/bash
set -e

FECHA=$(date +%Y-%m-%d_%H:%M:%S)
MANIFEST="SOBERANO_01_MEMORIA/RESCATE/MANIFIESTO_TRASVASE_${FECHA}.md"

echo "======================================================"
echo "   📦 TRASVASE BASADO EN EVIDENCIA REAL (main -> v1)   "
echo "======================================================"

# 1. Crear las 4 estructuras departamentales
mkdir -p SOBERANO_00_GOBIERNO/DOCS/seguridad
mkdir -p SOBERANO_01_MEMORIA/RESCATE
mkdir -p SOBERANO_01_MEMORIA/AUDITS
mkdir -p SOBERANO_01_MEMORIA/ACTAS
mkdir -p SOBERANO_02_CORE/core
mkdir -p SOBERANO_02_CORE/workflows
mkdir -p SOBERANO_03_NEXUS/providers
mkdir -p SOBERANO_03_NEXUS/parliament
mkdir -p SOBERANO_03_NEXUS/telegram
mkdir -p SOBERANO_03_NEXUS/frontend

# 2. Iniciar Manifiesto de Evidencia
cat > "$MANIFEST" << EOF_MAN
---
id: TRASVASE-EVIDENCIA-${FECHA}
date: $(date +%Y-%m-%d)
type: Manifiesto_Trasvase
author: Mesa_Tecnica_EAD
---
# 📜 MANIFIESTO DE TRASVASE POR EVIDENCIA DIRECTA

Este documento certifica el trasvase físico de los archivos de la rama \`main\` a los 4 Departamentos Soberanos en \`soberano-v1\`.

## 📁 REGISTRO DE TRASLADOS REALIZADOS

EOF_MAN

# Función auxiliar para checkout y registro
trasvasar() {
    local origen="$1"
    local destino="$2"
    
    if git checkout origin/main -- "$origen" 2>/dev/null; then
        mkdir -p "$(dirname "$destino")"
        mv "$origen" "$destino"
        echo "- **Origen:** \`$origen\` ➡️ **Destino:** \`$destino\`" >> "$MANIFEST"
        echo " [OK] $origen -> $destino"
    else
        echo " [SKIP] No encontrado en origin/main: $origen"
    fi
}

echo ""
echo "--- 1. SOBERANO_00_GOBIERNO (Constitución y Normas) ---"
trasvasar "00-GOBIERNO/DOCS/constitucion.md" "SOBERANO_00_GOBIERNO/constitucion.md"
trasvasar "00-GOBIERNO/DOCS/roles.md" "SOBERANO_00_GOBIERNO/roles.md"
trasvasar "00-GOBIERNO/DOCS/seguridad/protocolo.md" "SOBERANO_00_GOBIERNO/DOCS/seguridad/protocolo.md"
trasvasar "00-GOBIERNO/DOCS/NEXUS_MANIFEST.json" "SOBERANO_00_GOBIERNO/NEXUS_MANIFEST.json"

echo ""
echo "--- 2. SOBERANO_01_MEMORIA (Actas, Documentación e Históricos) ---"
trasvasar "01-MEMORIA/DOCS/actas/NEXUS-DEB-20260630-0214.md" "SOBERANO_01_MEMORIA/ACTAS/NEXUS-DEB-20260630-0214.md"
trasvasar "04-REGISTROS/DOCS/bitacora.md" "SOBERANO_01_MEMORIA/bitacora.md"
trasvasar "04-REGISTROS/DOCS/contexto_nexus_20260705_1943.md" "SOBERANO_01_MEMORIA/contexto_nexus_20260705_1943.md"
trasvasar "05-DOCUMENTACION/DOCS/README.md" "SOBERANO_01_MEMORIA/README_LEGACY.md"
trasvasar "08-ARCHIVO/README.md" "SOBERANO_01_MEMORIA/ARCHIVO_README.md"

echo ""
echo "--- 3. SOBERANO_02_CORE (Motor Trading y Workflows) ---"
trasvasar "02-SISTEMA/API/api/core/scheduler.py" "SOBERANO_02_CORE/core/scheduler.py"
trasvasar "02-SISTEMA/API/api/core/generar_bitacora.py" "SOBERANO_02_CORE/core/generar_bitacora.py"
trasvasar ".github/workflows/worker.yml" ".github/workflows/worker.yml"

echo ""
echo "--- 4. SOBERANO_03_NEXUS (Conectores IA, API y Telegram) ---"
trasvasar "02-SISTEMA/API/api/providers/groq.py" "SOBERANO_03_NEXUS/providers/groq.py"
trasvasar "02-SISTEMA/API/api/providers/openrouter.py" "SOBERANO_03_NEXUS/providers/openrouter.py"
trasvasar "02-SISTEMA/API/api/router.py" "SOBERANO_03_NEXUS/router.py"
trasvasar "02-SISTEMA/API/api/index.py" "SOBERANO_03_NEXUS/index.py"
trasvasar "02-SISTEMA/API/api/parliament/manager.py" "SOBERANO_03_NEXUS/parliament/manager.py"
trasvasar "02-SISTEMA/API/api/telegram/utils.py" "SOBERANO_03_NEXUS/telegram/utils.py"
trasvasar "07-NEXUS-IA/frontend/index.html" "SOBERANO_03_NEXUS/frontend/index.html"
trasvasar "07-NEXUS-IA/frontend/js/app.js" "SOBERANO_03_NEXUS/frontend/app.js"

# Limpieza de directorios temporales creados por checkout
rm -rf 00-GOBIERNO 01-MEMORIA 02-SISTEMA 04-REGISTROS 05-DOCUMENTACION 07-NEXUS-IA 08-ARCHIVO 2>/dev/null || true

# 3. Confirmar cambios en Git
git add SOBERANO_00_GOBIERNO/ SOBERANO_01_MEMORIA/ SOBERANO_02_CORE/ SOBERANO_03_NEXUS/ .github/
git commit -m "[EAD] Trasvase sistematico con evidencia de main a soberano-v1" || true
git push origin soberano-v1

echo ""
echo "======================================================"
echo "✅ Trasvase completado con éxito."
echo "📄 Evidencia inmutable guardada en:"
echo "   $MANIFEST"
echo "======================================================"
