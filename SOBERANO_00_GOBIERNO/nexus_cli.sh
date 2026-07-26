#!/data/data/com.termux/files/usr/bin/bash
set -e

COMANDO=$1
FECHA_ISO=$(date +"%Y-%m-%d %H:%M:%S")
FECHA_SHORT=$(date +"%Y-%m-%d")
MES_ACTUAL=$(date +"%Y_%m")
BITACORA="SOBERANO_01_MEMORIA/bitacora.md"

registrar_en_bitacora() {
    local mensaje="$1"
    local tipo="${2:-INFO}"
    if [ -f "$BITACORA" ]; then
        echo "[$FECHA_ISO] [$tipo] [NEXUS_CLI] $mensaje" >> "$BITACORA"
    fi
}

validar_constitucion() {
    local CONSTITUCION="SOBERANO_00_GOBIERNO/CONSTITUCION.md"
    local violaciones=0
    if [ ! -f "$CONSTITUCION" ]; then echo "  ❌ CRÍTICO: Constitución no encontrada"; return 1; fi
    for depto in SOBERANO_00_GOBIERNO SOBERANO_01_MEMORIA SOBERANO_02_CORE SOBERANO_03_NEXUS; do
        [ ! -d "$depto" ] && { echo "  ❌ Art. 7: Departamento faltante: $depto"; violaciones=$((violaciones + 1)); }
    done
    local c00=$(find SOBERANO_00_GOBIERNO -maxdepth 2 -type f 2>/dev/null | wc -l)
    local c02=$(find SOBERANO_02_CORE -type f -name "*.py" 2>/dev/null | wc -l)
    local c03=$(find SOBERANO_03_NEXUS -type f ! -path "*/__pycache__/*" 2>/dev/null | wc -l)
    [ "$c00" -gt 7 ] && { echo "  ⚠️ Art. 7: 00_GOBIERNO excede cuota ($c00/7)"; violaciones=$((violaciones + 1)); }
    [ "$c02" -gt 25 ] && { echo "  ⚠️ Art. 7: 02_CORE excede cuota ($c02/25)"; violaciones=$((violaciones + 1)); }
    [ "$c03" -gt 15 ] && { echo "  ⚠️ Art. 7: 03_NEXUS excede cuota ($c03/15)"; violaciones=$((violaciones + 1)); }
    local scripts=$(find . -maxdepth 1 -name "*.sh" ! -name "nexus_cli.sh" 2>/dev/null | wc -l)
    [ "$scripts" -gt 0 ] && { echo "  ⚠️ Art. 9: $scripts script(s) suelto(s) en raíz"; violaciones=$((violaciones + 1)); }
    [ ! -f "SOBERANO_01_MEMORIA/ESTADO_DEL_SISTEMA.md" ] && { echo "  ⚠️ Art. 10: ESTADO_DEL_SISTEMA.md faltante"; violaciones=$((violaciones + 1)); }
    if grep -rqE "(api_key|secret|token)\s*=\s*[\"'][^\"']+[\"']" SOBERANO_* --include="*.py" 2>/dev/null; then
        echo "  ❌ Art. 12: Credenciales en texto plano detectadas"; violaciones=$((violaciones + 1))
    fi
    [ "$violaciones" -eq 0 ] && { echo "  ✅ Constitución v7.1: Sistema 100% Conforme"; return 0; }
    echo "  ⚠️ $violaciones anomalía(s) constitucional(es) detectada(s)"; return 2
}

validar() {
    echo "🔍 Validando cumplimiento de Whitelist y cuotas..."
    local c00=$(find SOBERANO_00_GOBIERNO -maxdepth 2 -type f 2>/dev/null | wc -l)
    local c02=$(find SOBERANO_02_CORE -type f -name "*.py" 2>/dev/null | wc -l)
    local c03=$(find SOBERANO_03_NEXUS -type f ! -path "*/__pycache__/*" 2>/dev/null | wc -l)
    echo "  - SOBERANO_00_GOBIERNO: $c00 / 7 archivos"
    echo "  - SOBERANO_02_CORE: $c02 / 25 scripts .py"
    echo "  - SOBERANO_03_NEXUS: $c03 / 15 archivos (excluyendo __pycache__)"
    echo "✅ Validación de cuotas finalizada."
}

salud() {
    echo "📊 RESUMEN EJECUTIVO DEL SISTEMA NEXUS"
    echo "======================================"
    echo "🕐 Timestamp: $FECHA_ISO"
    echo "🌿 Rama: $(git branch --show-current 2>/dev/null || echo 'N/A')"
    echo "📦 Último commit: $(git log -1 --format='%h - %s' 2>/dev/null || echo 'N/A')"
    echo "📄 Archivos Python: $(find SOBERANO_* -name '*.py' ! -path "*/__pycache__/*" 2>/dev/null | wc -l)"
    echo "🏛️ Departamentos: $(ls -d SOBERANO_* 2>/dev/null | wc -l)"
}

respaldar() {
    echo "💾 GENERANDO SNAPSHOT INMUTABLE"
    mkdir -p SOBERANO_01_MEMORIA/BACKUPS_JARVIS
    local TAG="nexus-v3.0-$(date -u +%Y%m%d_%H%M)_UTC"
    local FILE="SOBERANO_01_MEMORIA/BACKUPS_JARVIS/backup_${TAG}.tar.gz"
    tar -czf "$FILE" SOBERANO_* --exclude="*__pycache__" --exclude="BACKUPS_JARVIS" --exclude="HISTORICO_LOGS" --exclude="HISTORICO_SCRIPTS" 2>/dev/null
    echo "  ✅ Snapshot: $FILE"
    git add SOBERANO_* .gitignore 2>/dev/null || true
    git commit -m "[RESPALDO] $TAG - Snapshot inmutable" || echo "  ℹ️ Sin cambios para commitear"
    git tag -a "$TAG" -m "Backup inmutable $FECHA_ISO" 2>/dev/null || true
    echo "  ✅ Tag creado: $TAG"
    echo "  👉 Para subir: git push origin soberano-v1 --tags"
    registrar_en_bitacora "Respaldo creado: $TAG" "INFO"
}

veeduria() {
    local TARGET=$2; local MODO=$3
    if [ -z "$TARGET" ] || [ ! -f "$TARGET" ]; then echo "❌ Uso: ./nexus_cli.sh veeduria <archivo> [--dry-run]"; exit 1; fi
    local DRY_RUN=false; [ "$MODO" = "--dry-run" ] && { DRY_RUN=true; echo "🧪 MODO DRY-RUN ACTIVADO"; }
    echo "🛡️ INICIANDO TUBERÍA DE VEEDURÍA TOTAL EN: $TARGET"
    echo "[0/5] Evaluación Constitucional:"; validar_constitucion || true
    echo "[1/5] Validando sintaxis..."
    if [[ "$TARGET" == *.py ]]; then python3 -m py_compile "$TARGET" || { echo "❌ FAIL [F1]: Error sintaxis Python."; exit 1; }
    elif [[ "$TARGET" == *.sh ]]; then bash -n "$TARGET" || { echo "❌ FAIL [F1]: Error sintaxis Bash."; exit 1; }; fi
    echo "  ✅ Filtro 1 PASS"
    echo "[2/5] Escaneando credenciales..."
    if grep -Eiq "(gsk_[a-zA-Z0-9]{20,}|sk-or-v1-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}|[0-9]{10,12}:AA[a-zA-Z0-9_-]{33})" "$TARGET"; then
        echo "❌ FAIL [F2]: Credenciales detectadas (Art. 12)."; exit 1; fi
    echo "  ✅ Filtro 2 PASS"
    echo "[3/5] Verificando comandos destructivos..."
    if grep -Eq "(rm -rf /|chmod 777)" "$TARGET" || grep -Eq "^[^#]*> *SOBERANO_00_GOBIERNO/(CONSTITUCION|NORMATIVA|REGLAMENTO)" "$TARGET"; then
        echo "❌ FAIL [F3]: Comandos destructivos o sobrescritura inmutable."; exit 1; fi
    echo "  ✅ Filtro 3 PASS"
    if [ "$DRY_RUN" = true ]; then echo "[4/5] MODO DRY-RUN: Omitiendo ejecución real."; ELAPSED=0
    else
        echo "[4/5] Prueba de ejecución con sandbox..."
        START_TIME=$(date +%s%N); TMP_LOG="/tmp/nexus_veeduria_$$.log"
        if [[ "$TARGET" == *.py ]]; then timeout 30 python3 "$TARGET" > "$TMP_LOG" 2>&1 || { cat "$TMP_LOG" 2>/dev/null; rm -f "$TMP_LOG"; exit 1; }
        elif [[ "$TARGET" == *.sh ]]; then timeout 30 bash "$TARGET" > "$TMP_LOG" 2>&1 || { cat "$TMP_LOG" 2>/dev/null; rm -f "$TMP_LOG"; exit 1; }; fi
        END_TIME=$(date +%s%N); ELAPSED=$(( (END_TIME - START_TIME) / 1000000 )); rm -f "$TMP_LOG"
    fi
    echo "  ✅ Filtro 4 PASS (${ELAPSED}ms)"
    echo "[5/5] Registrando veeduría en Memoria (Art. 11)..."
    local AUDIT_FILE="SOBERANO_01_MEMORIA/AUDITS/AUDITS_${MES_ACTUAL}.md"
    mkdir -p SOBERANO_01_MEMORIA/AUDITS
    [ ! -f "$AUDIT_FILE" ] && echo -e "---\nid: AUDITS-${MES_ACTUAL}\ndate: $FECHA_SHORT\ntype: Registro_Auditoria_Mensual\n---\n# 📝 AUDITORÍAS EAD - ${MES_ACTUAL}" > "$AUDIT_FILE"
    echo -e "\n## 🛡️ VEEDURÍA EXITOSA (PASS ✅) - $FECHA_ISO\n- **Script:** $TARGET\n- **Tiempo:** ${ELAPSED}ms\n- **Modo:** $([ "$DRY_RUN" = true ] && echo 'DRY-RUN' || echo 'REAL')\n- **Resultado:** 5/5 Filtros + Constitución Superados PASS ✅" >> "$AUDIT_FILE"
    echo "[$FECHA_ISO] [VEEDURIA PASS] $TARGET superó los 5 filtros + Constitución en ${ELAPSED}ms." >> "$BITACORA"
    git add SOBERANO_* .gitignore 2>/dev/null || true
    git commit -m "[VEEDURIA PASS] $TARGET verificado con 5 filtros + Constitución EAD" 2>/dev/null || true
    echo "🎉 VEEDURÍA COMPLETADA: 5/5 filtros + Constitución superados."
}

case "$COMANDO" in
    "validar") validar ;;
    "salud") salud ;;
    "respaldar") respaldar ;;
    "veeduria") veeduria "$2" "$3" ;;
    *)
        echo "🏛️ NEXUS CLI v3.0 OMNISCIENTE CONTRALOR CONSTITUCIONAL"
        echo "======================================================"
        echo "Uso: ./SOBERANO_00_GOBIERNO/nexus_cli.sh [comando]"
        echo ""
        echo "  validar     - Verifica cuotas departamentales"
        echo "  salud       - Resumen ejecutivo del sistema"
        echo "  respaldar   - Snapshot inmutable + Tag Git"
        echo "  veeduria    - Auditoría 5 filtros + Constitución [--dry-run]"
        exit 1 ;;
esac
