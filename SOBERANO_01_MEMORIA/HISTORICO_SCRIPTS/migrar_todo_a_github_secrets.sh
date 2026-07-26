#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "======================================================"
echo "🔒 MIGRACIÓN MASIVA DE BÓVEDAS A GITHUB SECRETS"
echo "======================================================"
echo ""

ARCHIVOS_BOVEDA=(
    ".nexus_secrets"
    ".nexus/secrets.env"
    ".nexus/secrets.env.backup"
)

TOTAL_MIGRADOS=0

for archivo in "${ARCHIVOS_BOVEDA[@]}"; do
    if [ -f "$archivo" ]; then
        echo "📄 Procesando bóveda: $archivo"
        echo "------------------------------------------------------"
        
        while IFS= read -r linea || [ -n "$linea" ]; do
            # Limpiar espacios
            linea=$(echo "$linea" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
            
            # Ignorar líneas vacías o comentarios
            if [[ -z "$linea" || "$linea" == \#* ]]; then
                continue
            fi
            
            if [[ "$linea" == *"="* ]]; then
                LLAVE=$(echo "$linea" | cut -d'=' -f1 | xargs)
                VALOR=$(echo "$linea" | cut -d'=' -f2- | xargs)
                
                # Ignorar llaves vacías
                if [ -n "$LLAVE" ] && [ -n "$VALOR" ]; then
                    echo -n "  • Cifrando y subiendo $LLAVE ... "
                    echo "$VALOR" | gh secret set "$LLAVE" 2>/dev/null || { echo "❌ FAIL"; continue; }
                    echo "✅ OK"
                    TOTAL_MIGRADOS=$((TOTAL_MIGRADOS + 1))
                fi
            fi
        done < "$archivo"
        echo ""
    fi
done

echo "======================================================"
echo "🎉 MIGRACIÓN FINALIZADA: $TOTAL_MIGRADOS secreto(s) guardados en GitHub Secrets"
echo "======================================================"

# Mover a histórico
mkdir -p SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS
mv migrar_todo_a_github_secrets.sh SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS/ 2>/dev/null || true
