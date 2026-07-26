#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "======================================================"
echo "   🔍 AUDITORÍA DE CONTENIDO DE BÓVEDAS (ART. 12)     "
echo "======================================================"
echo ""

ARCHIVOS_BOVEDA=(
    ".nexus/secrets.env"
    ".nexus/secrets.env.backup"
    ".nexus_secrets"
    ".env"
    ".termux_authinfo"
)

TOTAL_VARIABLES=0

for archivo in "${ARCHIVOS_BOVEDA[@]}"; do
    if [ -f "$archivo" ]; then
        echo "📂 ARCHIVO ENCONTRADO: $archivo"
        echo "------------------------------------------------------"
        
        while IFS= read -r linea || [ -n "$linea" ]; do
            # Ignorar líneas vacías o comentarios
            linea=$(echo "$linea" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
            if [[ -z "$linea" || "$linea" == \#* ]]; then
                continue
            fi
            
            # Formato LLAVE=VALOR
            if [[ "$linea" == *"="* ]]; then
                LLAVE=$(echo "$linea" | cut -d'=' -f1 | xargs)
                VALOR=$(echo "$linea" | cut -d'=' -f2- | xargs)
                LONGITUD=${#VALOR}
                
                if [ $LONGITUD -gt 0 ]; then
                    echo "  🔑 Variable: $LLAVE  --> [CONFIGURADA - $LONGITUD caracteres]"
                else
                    echo "  ⚠️ Variable: $LLAVE  --> [VACÍA]"
                fi
                TOTAL_VARIABLES=$((TOTAL_VARIABLES + 1))
            else
                # Caso de texto o token directo sin '='
                TIPO="Texto/String"
                LONGITUD=${#linea}
                echo "  📄 Registro directo ($TIPO)  --> [$LONGITUD caracteres]"
                TOTAL_VARIABLES=$((TOTAL_VARIABLES + 1))
            fi
        done < "$archivo"
        echo ""
    else
        echo "⚪ Archivo no presente: $archivo"
    fi
done

echo "======================================================"
echo "📊 RESUMEN: Se auditaron $TOTAL_VARIABLES secreto(s) en total."
echo "======================================================"

# Mover a histórico
mkdir -p SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS
mv inspeccionar_bovedas.sh SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS/ 2>/dev/null || true
