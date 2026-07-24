#!/data/data/com.termux/files/usr/bin/bash
set -e

FECHA=$(date +%Y-%m-%d_%H:%M:%S)
REPORT_FILE="SOBERANO_01_MEMORIA/AUDITS/AUDITORIA_TOTAL_CONSOLIDACION_${FECHA}.md"

echo "======================================================"
echo "   🔍 AUDITORÍA TOTAL DE ESTRUCTURA Y SINCRONIZACIÓN   "
echo "======================================================"
echo ""

echo "📌 1. RAMA ACTUAL Y ESTADO DE TRABAJO:"
git status -s -b

echo ""
echo "📌 2. VERIFICACIÓN DE CARPETAS DEPARTAMENTALES:"
for dept in SOBERANO_00_GOBIERNO SOBERANO_01_MEMORIA SOBERANO_02_CORE SOBERANO_03_NEXUS; do
    if [ -d "$dept" ]; then
        count=$(find "$dept" -type f | wc -l)
        echo "  [OK] $dept/ ($count archivos)"
    else
        echo "  [ERROR] $dept/ NO EXISTE"
    fi
done

echo ""
echo "📌 3. ESTRUCTURA COMPLETA INDEXADA EN GIT (soberano-v1):"
git ls-tree -r HEAD --name-only

# Guardar informe de auditoría
cat > "$REPORT_FILE" << EOF_AUDIT
---
id: AUDITORIA-TOTAL-${FECHA}
date: $(date +%Y-%m-%d)
type: Auditoria_Consolidacion
status: Exitoso
---
# 📜 REPORT DE AUDITORÍA TOTAL DE CONSOLIDACIÓN

**Fecha:** $FECHA  
**Rama:** $(git branch --show-current)  
**Último Commit:** $(git rev-parse --short HEAD)  

## 📂 INVENTARIO POR DEPARTAMENTO

### SOBERANO_00_GOBIERNO
\`\`\`
$(git ls-tree -r HEAD SOBERANO_00_GOBIERNO --name-only 2>/dev/null)
\`\`\`

### SOBERANO_01_MEMORIA
\`\`\`
$(git ls-tree -r HEAD SOBERANO_01_MEMORIA --name-only 2>/dev/null)
\`\`\`

### SOBERANO_02_CORE
\`\`\`
$(git ls-tree -r HEAD SOBERANO_02_CORE --name-only 2>/dev/null)
\`\`\`

### SOBERANO_03_NEXUS
\`\`\`
$(git ls-tree -r HEAD SOBERANO_03_NEXUS --name-only 2>/dev/null)
\`\`\`

EOF_AUDIT

git add "$REPORT_FILE"
git commit -m "[EAD] Registro de Auditoria Total de Consolidacion" || true
git push origin soberano-v1

echo ""
echo "======================================================"
echo "✅ Auditoría finalizada. Reporte registrado en:"
echo "   $REPORT_FILE"
echo "======================================================"
