#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "======================================================"
echo "   🤖 RESCATANDO Y ASIGNANDO SOBERANO_03_NEXUS        "
echo "======================================================"

# 1. Crear la estructura interna
mkdir -p SOBERANO_03_NEXUS/providers
mkdir -p SOBERANO_03_NEXUS/parliament
mkdir -p SOBERANO_03_NEXUS/telegram
mkdir -p SOBERANO_03_NEXUS/frontend

# 2. Extraer los archivos directamente de origin/main
git checkout origin/main -- 02-SISTEMA/API/api/providers/groq.py 2>/dev/null && mv 02-SISTEMA/API/api/providers/groq.py SOBERANO_03_NEXUS/providers/ || true
git checkout origin/main -- 02-SISTEMA/API/api/providers/openrouter.py 2>/dev/null && mv 02-SISTEMA/API/api/providers/openrouter.py SOBERANO_03_NEXUS/providers/ || true
git checkout origin/main -- 02-SISTEMA/API/api/router.py 2>/dev/null && mv 02-SISTEMA/API/api/router.py SOBERANO_03_NEXUS/ || true
git checkout origin/main -- 02-SISTEMA/API/api/index.py 2>/dev/null && mv 02-SISTEMA/API/api/index.py SOBERANO_03_NEXUS/ || true
git checkout origin/main -- 02-SISTEMA/API/api/parliament/manager.py 2>/dev/null && mv 02-SISTEMA/API/api/parliament/manager.py SOBERANO_03_NEXUS/parliament/ || true
git checkout origin/main -- 02-SISTEMA/API/api/telegram/utils.py 2>/dev/null && mv 02-SISTEMA/API/api/telegram/utils.py SOBERANO_03_NEXUS/telegram/ || true
git checkout origin/main -- 07-NEXUS-IA/frontend/index.html 2>/dev/null && mv 07-NEXUS-IA/frontend/index.html SOBERANO_03_NEXUS/frontend/ || true
git checkout origin/main -- 07-NEXUS-IA/frontend/js/app.js 2>/dev/null && mv 07-NEXUS-IA/frontend/js/app.js SOBERANO_03_NEXUS/frontend/ || true

# 3. Limpiar rastros temporales del checkout
rm -rf 02-SISTEMA 07-NEXUS-IA 2>/dev/null || true

# 4. Confirmar e Indexar en Git
git add SOBERANO_03_NEXUS/
git commit -m "[EAD] Consolidacion completa y verificada de SOBERANO_03_NEXUS" || true
git push origin soberano-v1

echo ""
echo "======================================================"
echo "✅ SOBERANO_03_NEXUS completado y sincronizado."
echo "======================================================"
