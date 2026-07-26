#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "======================================================"
echo "   🌐 ESCANEO GENERAL DE LÓGICA, ROLES Y TRADING      "
echo "======================================================"
echo ""

MES_ACTUAL=$(date +"%Y_%m")
FECHA_ISO=$(date +"%Y-%m-%d %H:%M:%S")

echo "📂 1. ARBOL COMPLETO DE CÓDIGO (.py, .js, .json):"
echo "------------------------------------------------------"
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.json" \) -not -path '*/.*' | sort

echo ""
echo "🧠 2. BÚSQUEDA GENERAL DE ROLES, PROMPTS Y AGENTES:"
echo "------------------------------------------------------"
grep -rnEi "(role|system_prompt|prompt|agente|ministro|gerente|arquitecto|analista|trader|parlamento|voter)" --include="*.py" --include="*.js" . || echo "No se hallaron coincidencias de roles."

echo ""
echo "📈 3. BÚSQUEDA DE MÓDULOS DE TRADING, NOTICIAS Y ESTRATEGIA:"
echo "------------------------------------------------------"
grep -rnEi "(alpaca|vix|buy|sell|order|news|sentiment|market|strategy|trade)" --include="*.py" --include="*.js" . || echo "No se hallaron coincidencias de trading."

# Mover a histórico
mkdir -p SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS
mv escaneo_general_sistema.sh SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS/ 2>/dev/null || true

echo ""
echo "======================================================"
echo "✅ ESCANEO GENERAL FINALIZADO"
echo "======================================================"
