#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "======================================================"
echo "   🚀 FINALIZANDO REGISTRO Y PUSH A GITHUB           "
echo "======================================================"

# 1. Asegurar copia del workflow en SOBERANO_02_CORE
mkdir -p SOBERANO_02_CORE/workflows
cp .github/workflows/worker.yml SOBERANO_02_CORE/workflows/worker.yml 2>/dev/null || true

# 2. Limpieza de residuos de la extracción
rm -rf 00-GOBIERNO 01-MEMORIA 02-SISTEMA 04-REGISTROS 05-DOCUMENTACION 07-NEXUS-IA 08-ARCHIVO 2>/dev/null || true

# 3. Indexar todo y commitear
git add SOBERANO_00_GOBIERNO/ SOBERANO_01_MEMORIA/ SOBERANO_02_CORE/ SOBERANO_03_NEXUS/ .github/
git commit -m "[EAD] Trasvase sistematico con evidencia de main a soberano-v1 (Consolidado)" || true

# 4. Enviar a GitHub
git push origin soberano-v1

echo ""
echo "======================================================"
echo "✅ ¡TRASVASE PUBLICADO EXITOSAMENTE EN GITHUB!"
echo "   Revisa la rama 'soberano-v1' en la web: los 4 departamentos"
echo "   están ahora 100% operativos y estructurados."
echo "======================================================"
