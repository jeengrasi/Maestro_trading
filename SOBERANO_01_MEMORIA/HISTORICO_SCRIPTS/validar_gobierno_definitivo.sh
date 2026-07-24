#!/data/data/com.termux/files/usr/bin/bash
set -e

DEPT="SOBERANO_00_GOBIERNO"
FECHA_ISO=$(date +"%Y-%m-%d %H:%M:%S")
FECHA_FILE=$(date +%Y-%m-%d_%H-%M-%S)
REPORT_DIR="SOBERANO_01_MEMORIA/AUDITS"
REPORT_FILE="$REPORT_DIR/VALIDACION_GOBIERNO_${FECHA_FILE}.md"

echo "======================================================"
echo "   🔍 VALIDACIÓN DEFINITIVA DE $DEPT                  "
echo "======================================================"

# 1. Asegurar directorios de soporte
mkdir -p "$DEPT/DOCS/seguridad" "$REPORT_DIR"

ERRORES=0

# Detectar intérprete Python en Termux
PYTHON_BIN=""
if command -v python3 &> /dev/null; then
    PYTHON_BIN="python3"
elif command -v python &> /dev/null; then
    PYTHON_BIN="python"
fi

# 2. Inspección flexible de archivos (Insensible a mayúsculas/minúsculas)
echo "📌 1. Verificando presencia de componentes normativos..."
PATRONES=(
    "constitucion.md"
    "roles.md"
    "protocolo.md"
    "NEXUS_MANIFEST.json"
)

for patron in "${PATRONES[@]}"; do
    HALLAZGO=$(find "$DEPT" -iname "$patron" 2>/dev/null | head -1)
    if [ -n "$HALLAZGO" ]; then
        echo "  [OK] Encontrado: $HALLAZGO"
    else
        echo "  [WARN] Faltante: $patron"
        ERRORES=$((ERRORES + 1))
    fi
done

# 3. Validación de sintaxis JSON del Manifiesto
echo ""
echo "📌 2. Validando sintaxis de NEXUS_MANIFEST.json..."
MANIFEST=$(find "$DEPT" -iname "NEXUS_MANIFEST.json" 2>/dev/null | head -1)
if [ -n "$MANIFEST" ]; then
    if [ -n "$PYTHON_BIN" ]; then
        if $PYTHON_BIN -c "import json; json.load(open('$MANIFEST'))" 2>/dev/null; then
            echo "  [OK] Manifiesto JSON válido ($MANIFEST)."
        else
            echo "  [ERROR] Manifiesto JSON corrupto."
            ERRORES=$((ERRORES + 1))
        fi
    else
        echo "  [WARN] Python no instalado. Omitiendo prueba de JSON."
    fi
else
    echo "  [WARN] NEXUS_MANIFEST.json no localizado en $DEPT."
fi

# 4. Generación de Acta de Auditoría (EAD)
cat > "$REPORT_FILE" << EOF_REPORT
---
id: VAL-GOB-${FECHA_FILE}
date: $FECHA_ISO
type: Validacion_Departamento
status: $([ $ERRORES -eq 0 ] && echo "APROBADO" || echo "CON_ADVERTENCIAS")
---
# 📜 REPORTE DE VALIDACIÓN: $DEPT

- **Fecha de Inspección:** $FECHA_ISO
- **Intérprete Python:** ${PYTHON_BIN:-"No disponible"}
- **Advertencias / Errores:** $ERRORES
- **Estado General:** $([ $ERRORES -eq 0 ] && echo "PASS ✅" || echo "WARN ⚠️")

## 📂 Inventario Inspeccionado
EOF_REPORT

for patron in "${PATRONES[@]}"; do
    HALLAZGO=$(find "$DEPT" -iname "$patron" 2>/dev/null | head -1)
    if [ -n "$HALLAZGO" ]; then
        echo "- [x] \`$HALLAZGO\`" >> "$REPORT_FILE"
    else
        echo "- [ ] \`$patron\` (Faltante)" >> "$REPORT_FILE"
    fi
done

# 5. Sincronizar en Git
git add "$REPORT_FILE" "$DEPT/" 2>/dev/null || true
git commit -m "[EAD] Validacion Departamento 00 (Gobierno) - $FECHA_FILE" || true
git push origin soberano-v1

echo ""
echo "======================================================"
if [ $ERRORES -eq 0 ]; then
    echo "✅ $DEPT validado al 100% sin observaciones."
else
    echo "⚠️ $DEPT completado con $ERRORES advertencia(s)."
fi
echo "📄 Reporte de evidencia inmutable guardado en:"
echo "   $REPORT_FILE"
echo "======================================================"
