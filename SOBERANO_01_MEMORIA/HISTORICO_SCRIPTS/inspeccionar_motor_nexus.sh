#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "======================================================"
echo "   🔍 LECTURA PROFUNDA DE LÓGICA EN SOBERANO_03_NEXUS "
echo "======================================================"
echo ""

ARCHIVOS=(
    "SOBERANO_03_NEXUS/index.py"
    "SOBERANO_03_NEXUS/router.py"
    "SOBERANO_03_NEXUS/parliament/manager.py"
    "SOBERANO_03_NEXUS/providers/groq.py"
    "SOBERANO_03_NEXUS/providers/openrouter.py"
)

for arch in "${ARCHIVOS[@]}"; do
    if [ -f "$arch" ]; then
        echo "======================================================"
        echo "📄 ARCHIVO: $arch"
        echo "======================================================"
        cat "$arch"
        echo ""
        echo ""
    fi
done

# Mover a histórico
mkdir -p SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS
mv inspeccionar_motor_nexus.sh SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS/ 2>/dev/null || true
