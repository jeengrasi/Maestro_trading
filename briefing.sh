#!/bin/bash
# ═══════════════════════════════════════════════════
# BRIEFING AUTOMÁTICO DEL SISTEMA MAESTRO-NEXUS
# ═══════════════════════════════════════════════════

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║  📊 BRIEFING DEL SISTEMA MAESTRO-NEXUS            ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# Leer ESTADO_DEL_SISTEMA.md
if [ -f "ESTADO_DEL_SISTEMA.md" ]; then
    echo "✅ Estado del sistema:"
    grep -A 2 "ÚLTIMO HECHO" ESTADO_DEL_SISTEMA.md | tail -n 1 | sed 's/^/   /'
    echo ""
    echo "⏳ Pendientes reales:"
    grep -A 5 "PENDIENTES REALES" ESTADO_DEL_SISTEMA.md | grep -E "^\s*\d\." | sed 's/^/   /'
else
    echo "❌ ERROR: ESTADO_DEL_SISTEMA.md no existe"
fi

echo ""

# Validar integridad de bitácora
python3 validar_memoria.py

echo ""
echo "═══════════════════════════════════════════════════"
echo "¿En qué pendiente desea trabajar? (Ejecute: python3 bitacora.py --consulta)"
echo "═══════════════════════════════════════════════════"
