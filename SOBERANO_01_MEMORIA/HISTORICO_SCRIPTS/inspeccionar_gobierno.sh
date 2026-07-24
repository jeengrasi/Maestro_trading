#!/data/data/com.termux/files/usr/bin/bash
set -e

DEPT="SOBERANO_00_GOBIERNO"

echo "======================================================"
echo "   🏛️ INSPECCIÓN DETALLADA: $DEPT"
echo "======================================================"
echo ""

echo "📌 1. ARBOL FÍSICO DE ARCHIVOS EN $DEPT:"
find "$DEPT" -type f | sed 's/^/  / '

echo ""
echo "======================================================"
echo "📌 2. CONTENIDO INICIAL Y REGLAS DE CADA ARCHIVO:"
echo "======================================================"

for f in $(find "$DEPT" -type f); do
    echo ""
    echo "📄 ARCHIVO: $f"
    echo "------------------------------------------------------"
    head -n 15 "$f" | sed 's/^/  | /'
    echo "------------------------------------------------------"
done

