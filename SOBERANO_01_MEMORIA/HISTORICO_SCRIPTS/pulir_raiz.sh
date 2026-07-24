#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "🧹 Eliminando carpetas temporales legacy del índice..."
git rm -rf 00-GOBIERNO 01-MEMORIA 02-SISTEMA 04-REGISTROS 05-DOCUMENTACION 08-ARCHIVO 2>/dev/null || true

git commit -m "[EAD] Limpieza de temporales legacy en raiz" || true
git push origin soberano-v1

echo "✨ ¡Raíz del repositorio 100% purificada!"
