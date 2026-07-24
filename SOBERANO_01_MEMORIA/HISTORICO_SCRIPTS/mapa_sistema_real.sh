#!/data/data/com.termux/files/usr/bin/bash
set -e

FECHA=$(date +%Y-%m-%d_%H:%M:%S)
MAPA_FILE="SOBERANO_01_MEMORIA/MAPA_SISTEMA_REAL.md"

mkdir -p SOBERANO_01_MEMORIA

cat > "$MAPA_FILE" << EOF_REPORT
---
id: MAPA-SISTEMA-${FECHA}
date: $(date +%Y-%m-%d)
type: Mapa_Estructural_Real
fuente: Sistema_de_Archivos_Nativo
---
# 🗺️ MAPA DE TOPOGRAFÍA REAL DEL SISTEMA

**Fecha de extracción:** $FECHA
**Rama activa:** $(git branch --show-current)
**Último commit:** $(git rev-parse HEAD)

---

## 1. TOPOLOGÍA DE RAMAS Y TAGS EN GITHUB (REMOTO)

### 🟢 Ramas Remotas Vivas:
\`\`\`
$(git ls-remote --heads origin | awk '{print $2}' | sed 's|refs/heads/||')
\`\`\`

### 🏷️ Tags de Respaldo Registrados:
\`\`\`
$(git ls-remote --tags origin | awk '{print $2}' | sed 's|refs/tags/||')
\`\`\`

---

## 2. ÁRBOL COMPLETO DE ARCHIVOS RASTREADOS EN GITHUB (INDEX)

\`\`\`
$(git ls-tree -r HEAD --name-only)
\`\`\`

---

## 3. ESTRUCTURA FÍSICA DE DIRECTORIOS EN DISCO (LOCAL)

\`\`\`
$(find . -maxdepth 3 -not -path '*/.*' | sort)
\`\`\`

---

## 4. INVENTARIO DE JOYAS Y ARCHIVOS CLAVE DETECTADOS

\`\`\`
$(git ls-tree -r HEAD --name-only | grep -E "scheduler|worker|generar_bitacora|EVIDENCIA|CONSTITUCION|index\.py|router\.py" || echo "Ningún archivo clave detectado")
\`\`\`
EOF_REPORT

git add "$MAPA_FILE"
git commit -m "[EAD] Mapa de topografía real generado directamente del sistema" || true
git push origin soberano-v1
