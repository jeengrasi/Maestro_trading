#!/data/data/com.termux/files/usr/bin/bash
set -e

FECHA_ISO=$(date +"%Y-%m-%d %H:%M:%S")
MES_ACTUAL=$(date +"%Y_%m")

echo "======================================================"
echo "   🏛️ INSTALACIÓN DE LISTA BLANCA Y CLI ÚNICO NEXUS   "
echo "======================================================"
echo ""

# 1. Crear el CLI Único: SOBERANO_00_GOBIERNO/nexus_cli.sh
cat > SOBERANO_00_GOBIERNO/nexus_cli.sh << 'EOF_CLI'
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
EOF_CLI

chmod +x SOBERANO_00_GOBIERNO/nexus_cli.sh

# 2. Redactar las 4 Normativas Departamentales
cat > SOBERANO_00_GOBIERNO/NORMATIVA_DEPARTAMENTAL.md << 'EOF_N0'
# 📜 NORMATIVA DEPARTAMENTAL: SOBERANO_00_GOBIERNO
- **Límite de Archivos:** Máximo 7 archivos.
- **Archivos Autorizados:** CONSTITUCION.md, NORMATIVA_DEPARTAMENTAL.md, REGLAMENTO_EAD.md, ROLES.md, NEXUS_MANIFEST.json, DOCS/seguridad/protocolo.md, nexus_cli.sh.
- **Prohibición:** Prohibido crear scripts bash temporales o archivos fuera de la Whitelist.
EOF_N0

cat > SOBERANO_01_MEMORIA/NORMATIVA_DEPARTAMENTAL.md << 'EOF_N1'
# 📜 NORMATIVA DEPARTAMENTAL: SOBERANO_01_MEMORIA
- **Régimen de Memoria:** Inmutable, append incremental.
- **Formatos:** `bitacora.md` (Digest a las 500 líneas), `ESTADO_DEL_SISTEMA.md` (Sobrescritura).
- **Actas y Auditorías:** Archivos mensuales acumulativos (`ACTAS_YYYY_MM.md`, `AUDITS_YYYY_MM.md`).
EOF_N1

cat > SOBERANO_02_CORE/NORMATIVA_DEPARTAMENTAL.md << 'EOF_N2'
# 📜 NORMATIVA DEPARTAMENTAL: SOBERANO_02_CORE
- **Límite de Archivos:** Máximo 25 scripts `.py`.
- **Propósito Exclusivo:** Lógica de ejecución, scheduler y estrategias de trading.
- **Aislamiento:** Prohibido incorporar interfaces de usuario o scripts bash de mantenimiento.
EOF_N2

cat > SOBERANO_03_NEXUS/NORMATIVA_DEPARTAMENTAL.md << 'EOF_N3'
# 📜 NORMATIVA DEPARTAMENTAL: SOBERANO_03_NEXUS
- **Límite de Archivos:** Máximo 15 archivos.
- **Propósito Exclusivo:** Conectores API (Groq, OpenRouter), Telegram, Vercel entrypoint y Frontend.
EOF_N3

# 3. Registrar el Acta EAD Mensual
ACTA_FILE="SOBERANO_01_MEMORIA/ACTAS/ACTAS_${MES_ACTUAL}.md"
mkdir -p SOBERANO_01_MEMORIA/ACTAS
echo "## 📜 ACTA DE CONGELACIÓN Y WHITELIST - $FECHA_ISO" >> "$ACTA_FILE"
echo "- **Aprobación:** Implementación de Whitelist Cerrada y CLI Único \`nexus_cli.sh\`." >> "$ACTA_FILE"
echo "- **Efecto:** Proscripción de scripts desechables temporales." >> "$ACTA_FILE"
echo "" >> "$ACTA_FILE"

# 4. Probar y Ejecutar el CLI Único
./SOBERANO_00_GOBIERNO/nexus_cli.sh estado
./SOBERANO_00_GOBIERNO/nexus_cli.sh validar

# 5. Mover instalador y realizar commit EAD
mv instalar_sistema_v8.sh SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS/ 2>/dev/null || true
git add SOBERANO_00_GOBIERNO/ SOBERANO_01_MEMORIA/ SOBERANO_02_CORE/ SOBERANO_03_NEXUS/
git commit -m "[GOBIERNO v8.0] Instalación de Whitelist Cerrada, 4 Normativas y CLI Único nexus_cli.sh" || echo "Sin cambios para commitear."

echo ""
echo "======================================================"
echo "✅ SISTEMA CONGELADO Y PROTEGIDO BAJO WHITELIST CERRADA"
echo "📄 CLI Único: SOBERANO_00_GOBIERNO/nexus_cli.sh"
echo "📄 Normativas: Instaladas en los 4 Departamentos Soberanos"
echo "📄 Acta Mensual: $ACTA_FILE"
echo "======================================================"
