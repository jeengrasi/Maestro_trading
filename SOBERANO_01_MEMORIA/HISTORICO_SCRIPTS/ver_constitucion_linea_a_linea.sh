#!/data/data/com.termux/files/usr/bin/bash
set -e

FILE="SOBERANO_00_GOBIERNO/CONSTITUCION.md"

echo "======================================================"
echo "   🔍 INSPECCIÓN REAL LÍNEA A LÍNEA (PROTOCOLO EAD)   "
echo "======================================================"
echo "📄 ARCHIVO: $FILE"
echo "======================================================"
echo ""

if [ -f "$FILE" ]; then
    # Imprime el archivo con numeración de líneas real
    nl -ba -s": " "$FILE"
    echo ""
    echo "======================================================"
    echo "✅ FIN DE LECTURA FÍSICA DIRECTA DE DISCO"
    echo "======================================================"
else
    echo "❌ ERROR: El archivo $FILE no existe en el disco."
    echo "======================================================"
    exit 1
fi
