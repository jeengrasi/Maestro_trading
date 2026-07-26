#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "======================================================"
echo "   🧹 SANAMIENTO DE GIT Y PROTECCIÓN DE ARTIFACTS    "
echo "======================================================"
echo ""

# 1. Crear / Actualizar .gitignore
cat > .gitignore << 'EOF_GITIGNORE'
# Archivos de sistema y entorno
.cache/
.npm/
.lesshst
.termux/
.termux_backup_temp/
.tor/
node_modules/

# Credenciales y Secretos (Art. 12)
*.env
*.env.backup
.nexus/
.nexus_secrets
.git-credentials
.termux_authinfo

# Temporales y Basura
/Archivado:
*.log
/tmp/
EOF_GITIGNORE

echo "✅ Arquitectura .gitignore actualizada."

# 2. Desmarcar archivos sensibles del área de staging de Git
git reset HEAD .
git add .gitignore SOBERANO_00_GOBIERNO/ SOBERANO_01_MEMORIA/ SOBERANO_02_CORE/ SOBERANO_03_NEXUS/

# 3. Mover scripts sueltos de la raíz a HISTORICO_SCRIPTS
mkdir -p SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS
for script in *.sh; do
    if [ -f "$script" ] && [ "$script" != "sanear_repositorio.sh" ]; then
        mv "$script" SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS/ 2>/dev/null || true
        echo "  -> Archivado: $script"
    fi
done

# Eliminar archivo erróneo si existe en raíz
rm -f "Archivado:" 2>/dev/null || true

# 4. Actualizar estado y registrar commit de saneamiento
mv sanear_repositorio.sh SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS/ 2>/dev/null || true
git commit -m "[GOBIERNO] Saneamiento de Git: .gitignore aplicado, secrets protegidos y raíz pulida" || echo "Sin cambios para commitear."

echo ""
echo "======================================================"
echo "✅ REPOSOTORIO SANEADO Y PROTEGIDO"
echo "📄 Gitignore: Aplicado contra credenciales y basura"
echo "📄 Raíz: Pulida bajo el Principio Anticaos (Art. 9)"
echo "======================================================"
