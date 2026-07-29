#!/bin/bash
# ==============================================================================
# SCRIPT DE AUDITORÍA Y EXTRACCIÓN DE CONTEXTO TOTAL - NEXUS SOBERANO
# ==============================================================================

OUTPUT="SOBERANO_01_MEMORIA/RESUMEN_EJECUTIVO_SISTEMA.md"

echo "# 🏛️ RESUMEN EJECUTIVO Y CONTEXTO DEL SISTEMA NEXUS" > "$OUTPUT"
echo "Generado automáticamente el: $(date -u '+%Y-%m-%d %H:%M:%S UTC')" >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 1. ESTADO DE GIT Y VERSIONES" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
git status >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
git log -n 5 --oneline >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 2. ESTRUCTURA DEL REPOSITORIO (DEPARTAMENTOS)" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
find . -maxdepth 2 -not -path '*/.*' -not -path './venv*' >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 3. INVENTARIO DE SCRIPTS DE GOBIERNO Y NÚCLEO" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
find SOBERANO_00_GOBIERNO SOBERANO_02_DEPARTAMENTOS SOBERANO_03_NEXUS -type f >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 4. RESPALDOS LOCALES DISPONIBLES (BACKUPS_JARVIS)" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
ls -lh SOBERANO_01_MEMORIA/BACKUPS_JARVIS/ 2>/dev/null >> "$OUTPUT" || echo "Sin respaldos locales en ruta." >> "$OUTPUT"
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "✅ Auditoría completada. Resumen guardado en: $OUTPUT"
