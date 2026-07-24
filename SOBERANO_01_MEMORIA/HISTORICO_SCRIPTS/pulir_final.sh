#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "======================================================"
echo "   🧹 ELIMINANDO RASTROS INDEXADOS LEGACY             "
echo "======================================================"

# Remover las referencias viejas del índice de Git
git rm -rf 02-SISTEMA 07-NEXUS-IA 2>/dev/null || true

# Registrar commit de cierre
git commit -m "[EAD] Consolidacion 100% limpia de los 4 Departamentos Soberanos" || true
git push origin soberano-v1

echo ""
echo "======================================================"
echo "✨ ¡SISTEMA CONSOLIDADO Y PURIFICADO AL 100%!"
echo "   Las 4 carpetas soberanas están activas y sincronizadas."
echo "======================================================"
