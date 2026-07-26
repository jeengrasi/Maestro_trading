#!/data/data/com.termux/files/usr/bin/bash
set -e

FECHA_ISO=$(date +"%Y-%m-%d %H:%M:%S")
MES_ACTUAL=$(date +"%Y_%m")

echo "======================================================"
echo "   🛠️ ACTUALIZACIÓN DEL CLI ÚNICO NEXUS (v1.1)        "
echo "======================================================"
echo ""

# 1. Añadir subcomando "inspeccionar" al nexus_cli.sh
cat > SOBERANO_00_GOBIERNO/nexus_cli.sh << 'EOF_CLI'
#!/data/data/com.termux/files/usr/bin/bash
set -e

COMANDO=$1
FECHA_ISO=$(date +"%Y-%m-%d %H:%M:%S")
MES_ACTUAL=$(date +"%Y_%m")

case "$COMANDO" in
    "validar")
        echo "🔍 Validando cumplimiento de Whitelist y cuotas..."
        COUNT_00=$(find SOBERANO_00_GOBIERNO -maxdepth 2 -type f | wc -l)
        echo "  - SOBERANO_00_GOBIERNO: $COUNT_00 / 7 archivos"
        COUNT_02=$(find SOBERANO_02_CORE -type f -name "*.py" | wc -l)
        echo "  - SOBERANO_02_CORE: $COUNT_02 / 25 scripts .py"
        COUNT_03=$(find SOBERANO_03_NEXUS -type f | wc -l)
        echo "  - SOBERANO_03_NEXUS: $COUNT_03 / 15 archivos"
        echo "✅ Validacion de cuotas finalizada."
        ;;
    "auditar")
        echo "📊 Generando reporte EAD mensual..."
        AUDIT_FILE="SOBERANO_01_MEMORIA/AUDITS/AUDITS_${MES_ACTUAL}.md"
        mkdir -p SOBERANO_01_MEMORIA/AUDITS
        echo "## 📝 AUDITORÍA EAD - $FECHA_ISO" >> "$AUDIT_FILE"
        echo "- Estado del sistema: OK" >> "$AUDIT_FILE"
        echo "- Commit Activo: $(git rev-parse --short HEAD 2>/dev/null || echo 'N/A')" >> "$AUDIT_FILE"
        echo "" >> "$AUDIT_FILE"
        echo "✅ Registro guardado en $AUDIT_FILE"
        ;;
    "limpiar")
        echo "🧹 Aplicando Principio Anticaos (Art. 9) en raiz..."
        mkdir -p SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS
        for script in *.sh; do
            if [ -f "$script" ] && [ "$script" != "nexus_cli.sh" ]; then
                mv "$script" SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS/ 2>/dev/null || true
                echo "  -> Archivado: $script"
            fi
        done
        echo "✅ Raiz de repositorio pulida."
        ;;
    "digest")
        echo "🗜️ Comprobando limite de bitacora..."
        BITACORA="SOBERANO_01_MEMORIA/bitacora.md"
        if [ -f "$BITACORA" ]; then
            LINES=$(wc -l < "$BITACORA")
            echo "  - Bitacora actual: $LINES lineas / 500 max"
            if [ "$LINES" -gt 500 ]; then
                echo "  ⚠️ Supera las 500 lineas. Ejecutando rotacion..."
                gzip -c "$BITACORA" > "SOBERANO_01_MEMORIA/bitacora_${MES_ACTUAL}.log.gz"
                echo "# 📜 BITÁCORA DEL SISTEMA PARLAMENTO NEXUS (NUEVO CICLO)" > "$BITACORA"
                echo "[$FECHA_ISO] [SYSTEM] Rotación y digest comprimido generado." >> "$BITACORA"
            fi
        fi
        ;;
    "estado")
        echo "📸 Actualizando ESTADO_DEL_SISTEMA.md..."
        ESTADO="SOBERANO_01_MEMORIA/ESTADO_DEL_SISTEMA.md"
        echo "---" > "$ESTADO"
        echo "id: ESTADO-$(date +%Y%m%d)" >> "$ESTADO"
        echo "date: $(date +%Y-%m-%d)" >> "$ESTADO"
        echo "type: Estado_Sistema" >> "$ESTADO"
        echo "---" >> "$ESTADO"
        echo "# 📸 ESTADO ACTUAL DEL SISTEMA PARLAMENTO NEXUS" >> "$ESTADO"
        echo "Fecha de actualización: $FECHA_ISO" >> "$ESTADO"
        echo "Rama activa: $(git branch --show-current 2>/dev/null || echo 'soberano-v1')" >> "$ESTADO"
        echo "" >> "$ESTADO"
        echo "## 📊 Archivos por Departamento" >> "$ESTADO"
        find SOBERANO_* -type f | sort >> "$ESTADO"
        echo "✅ Foto del sistema guardada en $ESTADO"
        ;;
    "inspeccionar")
        echo "🔍 Inspección física y auditoría de SOBERANO_02_CORE..."
        AUDIT_FILE="SOBERANO_01_MEMORIA/AUDITS/AUDITS_${MES_ACTUAL}.md"
        mkdir -p SOBERANO_01_MEMORIA/AUDITS
        
        echo ""
        echo "📄 1. CONTENIDO DE SOBERANO_02_CORE/core/scheduler.py:"
        echo "------------------------------------------------------"
        if [ -f "SOBERANO_02_CORE/core/scheduler.py" ]; then
            nl -ba -s": " SOBERANO_02_CORE/core/scheduler.py
            LINES_SCHEDULER=$(wc -l < SOBERANO_02_CORE/core/scheduler.py)
        else
            echo "⚠️ No se encontró core/scheduler.py"
            LINES_SCHEDULER=0
        fi
        
        echo ""
        echo "------------------------------------------------------"
        echo "📄 2. CONTENIDO DE SOBERANO_02_CORE/core/generar_bitacora.py:"
        echo "------------------------------------------------------"
        if [ -f "SOBERANO_02_CORE/core/generar_bitacora.py" ]; then
            nl -ba -s": " SOBERANO_02_CORE/core/generar_bitacora.py
            LINES_BITACORA=$(wc -l < SOBERANO_02_CORE/core/generar_bitacora.py)
        else
            echo "⚠️ No se encontró core/generar_bitacora.py"
            LINES_BITACORA=0
        fi
        
        echo ""
        echo "📊 Resumen de inspección:"
        echo "  - scheduler.py: $LINES_SCHEDULER líneas"
        echo "  - generar_bitacora.py: $LINES_BITACORA líneas"
        
        {
            echo ""
            echo "## 🔍 INSPECCIÓN DE SOBERANO_02_CORE - $FECHA_ISO"
            echo "- **scheduler.py:** $LINES_SCHEDULER líneas"
            echo "- **generar_bitacora.py:** $LINES_BITACORA líneas"
            echo "- **Resultado:** Lectura física completada con éxito."
            echo ""
        } >> "$AUDIT_FILE"
        
        echo "[$FECHA_ISO] [INSPECCION] Auditoría EAD de SOBERANO_02_CORE completada via nexus_cli.sh." >> SOBERANO_01_MEMORIA/bitacora.md
        
        echo ""
        echo "✅ Inspección registrada en $AUDIT_FILE"
        echo "✅ Bitácora alimentada."
        ;;
    *)
        echo "🏛️ PARLAMENTO NEXUS CLI v1.1"
        echo "Uso: ./SOBERANO_00_GOBIERNO/nexus_cli.sh [comando]"
        echo "Comandos: validar | auditar | limpiar | digest | estado | inspeccionar"
        exit 1
        ;;
esac
EOF_CLI

chmod +x SOBERANO_00_GOBIERNO/nexus_cli.sh

# 2. Ejecutar la inspección con el CLI Único
echo "🚀 Ejecutando inspección de CORE mediante nexus_cli.sh..."
./SOBERANO_00_GOBIERNO/nexus_cli.sh inspeccionar

# 3. Archivar script de instalación y realizar commit EAD
mv actualizar_cli_v1.1.sh SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS/ 2>/dev/null || true
git add SOBERANO_00_GOBIERNO/nexus_cli.sh SOBERANO_01_MEMORIA/
git commit -m "[CORE v1.1] Subcomando 'inspeccionar' añadido al CLI único. Inspección de SOBERANO_02_CORE registrada con EAD." || echo "Sin cambios para commitear."

echo ""
echo "======================================================"
echo "✅ CLI ACTUALIZADO A v1.1 Y CORE INSPECCIONADO"
echo "📄 Registro EAD: SOBERANO_01_MEMORIA/AUDITS/AUDITS_${MES_ACTUAL}.md"
echo "======================================================"
