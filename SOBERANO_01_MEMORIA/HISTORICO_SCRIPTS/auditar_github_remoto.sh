#!/data/data/com.termux/files/usr/bin/bash
set -e

FECHA=$(date +%Y-%m-%d_%H:%M:%S)
REPORT_FILE="SOBERANO_01_MEMORIA/AUDITS/INVENTARIO_GITHUB_REMOTO_${FECHA}.md"

mkdir -p SOBERANO_01_MEMORIA/AUDITS

echo "======================================================"
echo "   🌐 INSPECCIÓN COMPLETA EN EL SERVIDOR DE GITHUB    "
echo "======================================================"
echo ""

# 1. Traer los metadatos más recientes de GitHub
echo "🔄 Sincronizando metadatos con origin..."
git fetch --all --prune --tags

echo ""
echo "=== 1. RAMAS REMOTAS EXISTENTES EN GITHUB ==="
git branch -r

echo ""
echo "=== 2. ETIQUETAS / TAGS DE RESPALDO EN GITHUB ==="
git tag -l

echo ""
echo "=== 3. ÁRBOL DE ARCHIVOS EN LA RAMA 'soberano-v1' (REMOTO) ==="
git ls-tree -r origin/soberano-v1 --name-only || echo "No se pudo leer origin/soberano-v1"

echo ""
echo "=== 4. ÁRBOL DE ARCHIVOS EN LA RAMA 'main' (REMOTO) ==="
git ls-tree -r origin/main --name-only || echo "No se pudo leer origin/main"

# 2. Guardar reporte inmutable
cat > "$REPORT_FILE" << EOF_REPORT
---
id: INVENTARIO-GITHUB-${FECHA}
date: $(date +%Y-%m-%d)
type: Inventario_Remoto_GitHub
author: Mesa_Tecnica_EAD
---
# 🌐 INVENTARIO TOTAL DE LO QUE EXISTE EN GITHUB

**Fecha de consulta:** $FECHA

## 1. RAMAS REMOTAS (origin)
\`\`\`
$(git branch -r)
\`\`\`

## 2. ETIQUETAS / TAGS (origin)
\`\`\`
$(git tag -l)
\`\`\`

## 3. ARCHIVOS EN origin/soberano-v1
\`\`\`
$(git ls-tree -r origin/soberano-v1 --name-only 2>/dev/null || echo "N/A")
\`\`\`

## 4. ARCHIVOS EN origin/main
\`\`\`
$(git ls-tree -r origin/main --name-only 2>/dev/null || echo "N/A")
\`\`\`
EOF_REPORT

git add "$REPORT_FILE"
git commit -m "[EAD] Reporte de inventario total remoto de GitHub registrado" || true
git push origin soberano-v1

echo ""
echo "======================================================"
echo "✅ Inspección finalizada. Reporte registrado en:"
echo "   $REPORT_FILE"
echo "======================================================"
