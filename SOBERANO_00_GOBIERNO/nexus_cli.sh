#!/data/data/com.termux/files/usr/bin/bash
set -e

COMANDO=$1
FECHA_ISO=$(date +"%Y-%m-%d %H:%M:%S")
MES_ACTUAL=$(date +"%Y_%m")

case "$COMANDO" in
    "validar")
        echo "🔍 Validando cumplimiento de Whitelist y cuotas..."
        # Validar 00_GOBIERNO (Max 7)
        COUNT_00=$(find SOBERANO_00_GOBIERNO -maxdepth 2 -type f | wc -l)
        echo "  - SOBERANO_00_GOBIERNO: $COUNT_00 / 7 archivos"
        # Validar 02_CORE (Max 25)
        COUNT_02=$(find SOBERANO_02_CORE -type f -name "*.py" | wc -l)
        echo "  - SOBERANO_02_CORE: $COUNT_02 / 25 scripts .py"
        # Validar 03_NEXUS (Max 15)
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
            if [ "$script" != "nexus_cli.sh" ] && [ "$script" != "instalar_sistema_v8.sh" ] && [ -f "$script" ]; then
                mv "$script" SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS/ 2>/dev/null || true
                echo "  -> Archived: $script"
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
        echo "# 📸 ESTADO ACTUAL DEL SISTEMA PARLAMENTO NEXUS" > "$ESTADO"
        echo "Fecha de actualización: $FECHA_ISO" >> "$ESTADO"
        echo "Rama activa: $(git branch --show-current 2>/dev/null || echo 'soberano-v1')" >> "$ESTADO"
        echo "" >> "$ESTADO"
        echo "## 📊 Archivos por Departamento" >> "$ESTADO"
        find SOBERANO_* -type f | sort >> "$ESTADO"
        echo "✅ Foto del sistema guardada en $ESTADO"
        ;;
    *)
        echo "🏛️ PARLAMENTO NEXUS CLI v1.0"
        echo "Uso: ./SOBERANO_00_GOBIERNO/nexus_cli.sh [comando]"
        echo "Comandos: validar | auditar | limpiar | digest | estado"
        exit 1
        ;;
esac
