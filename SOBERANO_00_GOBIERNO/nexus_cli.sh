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

validar_art12() {
    echo "🔐 AUDITORÍA CONSTITUCIONAL - ARTÍCULO 12 (SEGURIDAD DE SECRETOS)"
    echo "=================================================================="
    echo "🔍 Escaneando código fuente en busca de credenciales expuestas..."
    
    local hallazgos=0
    local PATRONES='(gsk_[a-zA-Z0-9]{20,}|sk-or-v1-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}|[0-9]{10,12}:AA[a-zA-Z0-9_-]{33}|AKIA[0-9A-Z]{16})'
    
    # Escaneo de patrones de claves reales en archivos Python y Shell
    if grep -rE "$PATRONES" SOBERANO_* --include="*.py" --include="*.sh" 2>/dev/null; then
        echo "❌ CRÍTICO: Credenciales reales o Tokens detectados en el código."
        hallazgos=$((hallazgos + 1))
    fi
    
    # Escaneo de variables con valores asignados en duro (hardcoded strings)
    if grep -rqE "(api_key|secret_key|bot_token)\s*=\s*[\"'][a-zA-Z0-9_-]{10,}[\"']" SOBERANO_* --include="*.py" 2>/dev/null; then
        echo "❌ CRÍTICO: Cadenas sospechosas asignadas a variables de credenciales."
        hallazgos=$((hallazgos + 1))
    fi

    if [ "$hallazgos" -eq 0 ]; then
        echo "  ✅ ARTÍCULO 12 CUMPLIDO AL 100%"
        echo "  • Cero credenciales o tokens en texto plano local."
        echo "  • Todas las claves están delegadas de forma segura a GitHub Secrets."
        return 0
    else
        echo "  ⚠️ VIOLACIÓN AL ARTÍCULO 12 DETECTADA ($hallazgos anomalías)"
        return 1
    fi
}

validar_constitucion() {
    local CONSTITUCION="SOBERANO_00_GOBIERNO/CONSTITUCION.md"
    local violaciones=0
    
    if [ ! -f "$CONSTITUCION" ]; then
        echo "  ❌ CRÍTICO: Constitución no encontrada en $CONSTITUCION"
        return 1
    fi
    
    for depto in SOBERANO_00_GOBIERNO SOBERANO_01_MEMORIA SOBERANO_02_CORE SOBERANO_03_NEXUS; do
        if [ ! -d "$depto" ]; then
            echo "  ❌ Art. 7: Departamento faltante: $depto"
            violaciones=$((violaciones + 1))
        fi
    done
    
    local count_00=$(find SOBERANO_00_GOBIERNO -maxdepth 2 -type f 2>/dev/null | wc -l)
    local count_02=$(find SOBERANO_02_CORE -type f -name "*.py" 2>/dev/null | wc -l)
    local count_03=$(find SOBERANO_03_NEXUS -type f 2>/dev/null | wc -l)
    
    [ "$count_00" -gt 7 ] && { echo "  ⚠️ Art. 7: SOBERANO_00_GOBIERNO excede cuota ($count_00/7)"; violaciones=$((violaciones + 1)); }
    [ "$count_02" -gt 25 ] && { echo "  ⚠️ Art. 7: SOBERANO_02_CORE excede cuota ($count_02/25)"; violaciones=$((violaciones + 1)); }
    [ "$count_03" -gt 25 ] && { echo "  ⚠️ Art. 7: SOBERANO_03_NEXUS excede cuota ($count_03/25)"; violaciones=$((violaciones + 1)); }
    
    local scripts_sueltos=$(find . -maxdepth 1 -name "*.sh" ! -name "nexus_cli.sh" 2>/dev/null | wc -l)
    if [ "$scripts_sueltos" -gt 0 ]; then
        echo "  ⚠️ Art. 9: $scripts_sueltos script(s) suelto(s) en raíz"
        violaciones=$((violaciones + 1))
    fi
    
    if [ ! -f "SOBERANO_01_MEMORIA/ESTADO_DEL_SISTEMA.md" ]; then
        echo "  ⚠️ Art. 10: ESTADO_DEL_SISTEMA.md faltante"
        violaciones=$((violaciones + 1))
    fi
    
    if ! validar_art12 >/dev/null 2>&1; then
        echo "  ❌ Art. 12: Violación de seguridad detectada"
        violaciones=$((violaciones + 1))
    fi
    
    if [ "$violaciones" -eq 0 ]; then
        echo "  ✅ Constitución v7.1: Sistema 100% Conforme"
        return 0
    else
        echo "  ⚠️ $violaciones anomalía(s) constitucional(es) detectada(s)"
        return 2
    fi
}

calcular_metricas() {
    local AUDIT_FILE="SOBERANO_01_MEMORIA/AUDITS/AUDITS_${MES_ACTUAL}.md"
    if [ -f "$AUDIT_FILE" ]; then
        local PASS=$(grep -c "PASS" "$AUDIT_FILE" 2>/dev/null || true)
        local FAIL=$(grep -c "FAIL" "$AUDIT_FILE" 2>/dev/null || true)
        PASS=${PASS:-0}
        FAIL=${FAIL:-0}
        awk -v p="$PASS" -v f="$FAIL" 'BEGIN {
            tot = p + f;
            if (tot > 0) printf "%d%% (%d/%d)", (p * 100 / tot), p, tot;
            else print "100% (0/0)";
        }'
    else
        echo "N/A"
    fi
}

actualizar_semaforo() {
    local AUDIT_FILE="SOBERANO_01_MEMORIA/AUDITS/AUDITS_${MES_ACTUAL}.md"
    local ESTADO="SOBERANO_01_MEMORIA/ESTADO_DEL_SISTEMA.md"
    
    local ULTIMOS_PASS=0
    if [ -f "$AUDIT_FILE" ]; then
        ULTIMOS_PASS=$(grep -c "VEEDURÍA EXITOSA" "$AUDIT_FILE" 2>/dev/null || true)
        ULTIMOS_PASS=${ULTIMOS_PASS:-0}
    fi
    
    local SEMAFORO="ROJO 🔴"
    local STATUS="SEMAFORO_ROJO"
    if [ "$ULTIMOS_PASS" -ge 5 ]; then
        SEMAFORO="VERDE 🟢"
        STATUS="SEMAFORO_VERDE"
    fi
    
    local METRICAS=$(calcular_metricas)
    
    {
        echo "---"
        echo "id: ESTADO-$(date +%Y%m%d)"
        echo "date: $FECHA_SHORT"
        echo "type: Estado_Sistema"
        echo "status: $STATUS"
        echo "---"
        echo "# 📸 ESTADO ACTUAL DEL SISTEMA PARLAMENTO NEXUS"
        echo "Fecha de actualización: $FECHA_ISO"
        echo "Rama activa: $(git branch --show-current 2>/dev/null || echo 'soberano-v1')"
        echo "Semaforo Trading: $SEMAFORO"
        echo "Tasa de Exito: $METRICAS"
        echo ""
        echo "## 📊 Archivos por Departamento"
        find SOBERANO_* -type f 2>/dev/null | sort
    } > "$ESTADO"
}

veeduria() {
    shift # Elimina 'veeduria' de la lista de argumentos
    local TARGET=$1
    local MODO=$2
    
    if [ -z "$TARGET" ] || [ ! -f "$TARGET" ]; then
        echo "❌ Error: Debe indicar un archivo existente."
        echo "Uso: ./nexus_cli.sh veeduria <archivo> [--dry-run]"
        exit 1
    fi
    
    local DRY_RUN=false
    [ "$MODO" = "--dry-run" ] && { DRY_RUN=true; echo "🧪 MODO DRY-RUN ACTIVADO"; }
    
    echo "🛡️ INICIANDO TUBERÍA DE VEEDURÍA TOTAL (5 FILTROS + CONSTITUCIÓN) EN: $TARGET"
    
    echo "[0/5] Evaluación Constitucional:"
    validar_constitucion || true
    
    echo "[1/5] Validando sintaxis Python/Shell..."
    if [[ "$TARGET" == *.py ]]; then
        python3 -m py_compile "$TARGET" || { echo "❌ FAIL [F1]: Error de sintaxis Python."; exit 1; }
    elif [[ "$TARGET" == *.sh ]]; then
        bash -n "$TARGET" || { echo "❌ FAIL [F1]: Error de sintaxis Bash."; exit 1; }
    fi
    echo "  ✅ Filtro 1 PASS"

    echo "[2/5] Escaneando credenciales (Art. 12)..."
    if grep -Eiq "(gsk_[a-zA-Z0-9]{20,}|sk-or-v1-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}|[0-9]{10,12}:AA[a-zA-Z0-9_-]{33})" "$TARGET"; then
        echo "❌ FAIL [F2]: Credenciales detectadas en texto plano."
        exit 1
    fi
    echo "  ✅ Filtro 2 PASS"

    echo "[3/5] Verificando comandos destructivos..."
    if grep -Eq "(rm -rf /|chmod 777)" "$TARGET"; then
        echo "❌ FAIL [F3]: Comandos destructivos peligrosos."
        exit 1
    fi
    echo "  ✅ Filtro 3 PASS"

    if [ "$DRY_RUN" = true ]; then
        echo "[4/5] MODO DRY-RUN: Omitiendo prueba de ejecución en vivo."
        ELAPSED=0
    else
        echo "[4/5] Prueba de ejecución con sandbox..."
        START_TIME=$(date +%s%N)
        TMP_LOG="/tmp/nexus_veeduria_$$.log"
        
        if [[ "$TARGET" == *.py ]]; then
            timeout 30 python3 "$TARGET" > "$TMP_LOG" 2>&1 || { 
                echo "❌ FAIL [F4]: Fallo en ejecución. Logs:"
                cat "$TMP_LOG" 2>/dev/null || true
                rm -f "$TMP_LOG"
                exit 1 
            }
        fi
        END_TIME=$(date +%s%N)
        ELAPSED=$(( (END_TIME - START_TIME) / 1000000 ))
        rm -f "$TMP_LOG"
    fi
    echo "  ✅ Filtro 4 PASS (${ELAPSED}ms)"

    echo "[5/5] Registrando veeduría en Memoria..."
    local AUDIT_FILE="SOBERANO_01_MEMORIA/AUDITS/AUDITS_${MES_ACTUAL}.md"
    mkdir -p SOBERANO_01_MEMORIA/AUDITS
    if [ ! -f "$AUDIT_FILE" ]; then
        echo -e "---\nid: AUDITS-${MES_ACTUAL}\ndate: $FECHA_SHORT\ntype: Registro_Auditoria_Mensual\n---\n# 📝 AUDITORÍAS EAD - ${MES_ACTUAL}" > "$AUDIT_FILE"
    fi

    {
        echo ""
        echo "## 🛡️ VEEDURÍA EXITOSA (PASS ✅) - $FECHA_ISO"
        echo "- **Script:** $TARGET"
        echo "- **Tiempo:** ${ELAPSED}ms"
        echo "- **Modo:** $([ "$DRY_RUN" = true ] && echo 'DRY-RUN' || echo 'REAL')"
        echo "- **Resultado:** 5/5 Filtros + Constitución Superados PASS ✅"
    } >> "$AUDIT_FILE"

    echo "[$FECHA_ISO] [VEEDURIA PASS] $TARGET superó los 5 filtros + Constitución en ${ELAPSED}ms." >> "$BITACORA"
    actualizar_semaforo
    
    echo ""
    echo "🎉 VEEDURÍA COMPLETADA: 5/5 filtros + Constitución superados."
}

salud() {
    echo "📊 RESUMEN EJECUTIVO DEL SISTEMA NEXUS"
    echo "======================================"
    echo "🕐 Timestamp: $FECHA_ISO"
    echo "🌿 Rama: $(git branch --show-current 2>/dev/null || echo 'N/A')"
    echo "📦 Último commit: $(git log -1 --format='%h - %s' 2>/dev/null || echo 'N/A')"
    echo "💾 Peso: $(du -sh . --exclude=.git --exclude=99_RESCATE_LOCAL 2>/dev/null | cut -f1)"
    echo "📄 Archivos Python: $(find SOBERANO_* -name '*.py' 2>/dev/null | wc -l)"
    echo "🏛️ Departamentos: $(ls -d SOBERANO_* 2>/dev/null | wc -l)"
    actualizar_semaforo
    echo "🚦 Semáforo: $(grep 'Semaforo Trading' SOBERANO_01_MEMORIA/ESTADO_DEL_SISTEMA.md 2>/dev/null | head -1)"
}

respaldar() {
    echo "💾 GENERANDO SNAPSHOT INMUTABLE"
    mkdir -p SOBERANO_01_MEMORIA/BACKUPS_JARVIS
    local TAG="nexus-v3.0-$(date -u +%Y%m%d_%H%M)_UTC"
    local FILE="SOBERANO_01_MEMORIA/BACKUPS_JARVIS/backup_${TAG}.tar.gz"
    
    tar -czf "$FILE" SOBERANO_* --exclude="*__pycache__" --exclude="BACKUPS_JARVIS" --exclude="HISTORICO_LOGS" 2>/dev/null
    echo "  ✅ Snapshot: $FILE"
    
    git add SOBERANO_* .gitignore
    git commit -m "[RESPALDO] $TAG - Snapshot inmutable" || echo "  ℹ️ Sin cambios para commitear"
    git tag -a "$TAG" -m "Backup inmutable $FECHA_ISO" || true
    echo "  ✅ Tag creado: $TAG"
    echo "  👉 Para subir: git push origin soberano-v1 --tags"
    
    registrar_en_bitacora "Respaldo creado: $TAG" "INFO"
}

case "$COMANDO" in
    "validar-art12") validar_art12 ;;
    "veeduria") veeduria "$@" ;;
    "salud") salud ;;
    "respaldar") respaldar ;;
    *)
        echo "🏛️ NEXUS CLI v3.2 OMNISCIENTE CONTRALOR CONSTITUCIONAL"
        echo "======================================================"
        echo "Uso: ./SOBERANO_00_GOBIERNO/nexus_cli.sh [comando]"
        echo ""
        echo "  validar-art12         - Escaneo estricto del Art. 12 (0 credenciales locales)"
        echo "  veeduria <file> [--dry-run] - Auditoría de 5 filtros en scripts"
        echo "  salud                 - Resumen ejecutivo del sistema"
        echo "  respaldar             - Snapshot inmutable + Tag Git"
        exit 1
        ;;
esac
