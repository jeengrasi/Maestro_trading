#!/data/data/com.termux/files/usr/bin/bash
set -e

FECHA_HOY=$(date +%Y-%m-%d)

echo "======================================================"
echo "   📖 INSPECCIÓN DE CONTENIDO Y FECHAS (2026)         "
echo "======================================================"
echo "Fecha actual del sistema: $FECHA_HOY"
echo ""

echo "--- 🏛️ 1. SOBERANO_00_GOBIERNO (Normas y Roles) ---"
for f in SOBERANO_00_GOBIERNO/constitucion.md SOBERANO_00_GOBIERNO/roles.md SOBERANO_00_GOBIERNO/DOCS/seguridad/protocolo.md SOBERANO_00_GOBIERNO/NEXUS_MANIFEST.json; do
    if [ -f "$f" ]; then
        echo "📄 Archivo: $f"
        echo "   Modificación local: $(date -r "$f" +"%Y-%m-%d %H:%M:%S")"
        echo "   Primeras 8 líneas de contenido:"
        head -n 8 "$f" | sed 's/^/   | /'
        echo "------------------------------------------------------"
    fi
done

echo ""
echo "--- 📜 2. SOBERANO_01_MEMORIA (Actas y Mapas) ---"
for f in SOBERANO_01_MEMORIA/MAPA_SISTEMA_REAL.md SOBERANO_01_MEMORIA/bitacora.md SOBERANO_01_MEMORIA/contexto_nexus_20260705_1943.md; do
    if [ -f "$f" ]; then
        echo "📄 Archivo: $f"
        echo "   Modificación local: $(date -r "$f" +"%Y-%m-%d %H:%M:%S")"
        echo "   Primeras 8 líneas de contenido:"
        head -n 8 "$f" | sed 's/^/   | /'
        echo "------------------------------------------------------"
    fi
done

