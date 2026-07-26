#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "======================================================"
echo "   🔬 AUDITORÍA CLINICA DE ROLES Y LÓGICA PARLAMENTARIA"
echo "======================================================"
echo ""

ARCHIVOS_PARLAMENTO=(
    "SOBERANO_03_NEXUS/parliament/core.py"
    "SOBERANO_03_NEXUS/parliament/debate.py"
    "SOBERANO_03_NEXUS/parliament/classifier.py"
    "SOBERANO_03_NEXUS/telegram/utils.py"
)

for arch in "${ARCHIVOS_PARLAMENTO[@]}"; do
    if [ -f "$arch" ]; then
        echo "======================================================"
        echo "📄 ARCHIVO: $arch"
        echo "======================================================"
        cat "$arch"
        echo ""
        echo ""
    else
        echo "⚠️ Archivo no encontrado: $arch"
    fi
done

# Mover a histórico
mkdir -p SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS
mv auditar_parlamento_completo.sh SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS/ 2>/dev/null || true
