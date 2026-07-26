#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "🔒 LEYENDO BÓVEDA Y CONECTANDO GITHUB CLI AUTOMÁTICAMENTE..."

# Archivos candidatos de la bóveda
BOVEDA_1=".nexus/secrets.env"
BOVEDA_2=".nexus_secrets"
BOVEDA_3=".env"

TOKEN=""

# Buscar variable de token de GitHub en la bóveda sin imprimirla
for archivo in "$BOVEDA_1" "$BOVEDA_2" "$BOVEDA_3"; do
    if [ -f "$archivo" ]; then
        # Buscar patrones comunes de variables de GitHub
        TOKEN=$(grep -E '^(GITHUB_TOKEN|GH_TOKEN|GITHUB_PAT|GH_PAT)=' "$archivo" | cut -d'=' -f2- | xargs 2>/dev/null || true)
        if [ -z "$TOKEN" ]; then
            # Buscar cualquier token que empiece por ghp_ o github_pat_
            TOKEN=$(grep -oE '(ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{22,})' "$archivo" | head -n 1 2>/dev/null || true)
        fi
        if [ -n "$TOKEN" ]; then
            echo "✅ Token localizado dentro de: $archivo"
            break
        fi
    fi
done

if [ -z "$TOKEN" ]; then
    echo "⚠️ No se encontró la variable GITHUB_TOKEN o un token 'ghp_' en tus archivos de la bóveda."
    echo "Revisa que tu bóveda contenga la línea: GITHUB_TOKEN=ghp_tuToken..."
    exit 1
fi

# Autenticar gh directamente en segundo plano sin pedir nada
echo "$TOKEN" | gh auth login --with-token 2>/dev/null

echo "🎉 Autenticación automática completada."
echo ""
echo "📊 Estado actual de la conexión:"
gh auth status

# Mover a histórico
mkdir -p SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS
mv conectar_gh_desde_boveda.sh SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS/ 2>/dev/null || true
