#!/bin/bash
# ==============================================================================
# SCRIPT DE MUESTREO TOTAL - LECTURA INTEGRAL DE LA MEMORIA DEL SISTEMA
# ==============================================================================

OUTPUT="SOBERANO_01_MEMORIA/MUESTREO_TOTAL_SISTEMA.md"

{
    echo "# 🏛️ MUESTREO INTEGRAL Y LITERAL DEL SISTEMA NEXUS"
    echo "Generado el: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo ""
    
    echo "=================================================================="
    echo "1. CONSTITUCIÓN MAGNA (SOBERANO_00_GOBIERNO/CONSTITUCION.md)"
    echo "=================================================================="
    cat SOBERANO_00_GOBIERNO/CONSTITUCION.md
    echo ""
    
    echo "=================================================================="
    echo "2. CONTEXTO HISTÓRICO Y CREDENCIALES (SOBERANO_01_MEMORIA/contexto_nexus_20260705_1943.md)"
    echo "=================================================================="
    cat SOBERANO_01_MEMORIA/contexto_nexus_20260705_1943.md
    echo ""
    
    echo "=================================================================="
    echo "3. NÚCLEO OPERATIVO INDEX.PY (SOBERANO_03_NEXUS/index.py)"
    echo "=================================================================="
    cat SOBERANO_03_NEXUS/index.py
    echo ""

} > "$OUTPUT"

echo "✅ Muestreo total completado con éxito en: $OUTPUT"
