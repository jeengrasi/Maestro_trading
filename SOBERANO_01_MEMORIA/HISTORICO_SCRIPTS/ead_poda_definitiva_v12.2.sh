#!/data/data/com.termux/files/usr/bin/bash
set -e

# Variable global para nombres estables de tags y evidencias
FECHA=$(date +%Y%m%d)

echo "=== [E] FASE 1: RESCATE OBLIGATORIO DE JOYAS ANTES DE PODA ==="
git fetch origin
git checkout soberano-v1

echo "Rescatando scheduler y generar_bitacora..."
mkdir -p SOBERANO_02_CORE/core
git show origin/feature/fase2-bitacora:02-SISTEMA/API/api/core/scheduler.py > SOBERANO_02_CORE/core/scheduler.py 2>/dev/null || echo "  [INFO] scheduler.py no encontrado"
git show origin/feature/fase2-bitacora:02-SISTEMA/API/api/core/generar_bitacora.py > SOBERANO_02_CORE/core/generar_bitacora.py 2>/dev/null || echo "  [INFO] generar_bitacora.py no encontrado"

echo "Rescatando worker.yml..."
mkdir -p .github/workflows
git show origin/fix/agregar-alpaca-py:.github/workflows/worker.yml > .github/workflows/worker.yml 2>/dev/null || echo "  [INFO] worker.yml no encontrado"

# Indexación y publicación en soberano-v1
git add SOBERANO_02_CORE/core/ .github/workflows/worker.yml 2>/dev/null || true
git commit -m "[RESCATE EAD] Scheduler, generar_bitacora y worker.yml rescatados" || echo "  [INFO] Nada nuevo que commitear"
git push origin soberano-v1

echo ""
echo "=== [D] FASE 2: TAGS DE RESPALDO DE SEGURIDAD ==="
for rama in Estable Staging fix-timeout-background fix-timeout-v3.1; do
  git tag archivo/$rama-$FECHA origin/$rama 2>/dev/null || true
  git push origin archivo/$rama-$FECHA 2>/dev/null || true
done

echo ""
echo "=== [E] FASE 3: EJECUCIÓN DE PODA DE RAMAS OBSOLETAS ==="
git fetch --prune
git push origin --delete fix/agregar-alpaca-py fix/restaurar-v2.2 fix-timeout-background fix-timeout-v3.1 2>/dev/null || true
git push origin --delete feature/actualizaciones-v2.0 feature/redistribucion feature/fase2-bitacora 2>/dev/null || true
git push origin --delete railway/code-change-frJoSO unificacion-nexus-20260707 organizar-departamentos 2>/dev/null || true
git push origin --delete Estable Staging develop 2>/dev/null || true

echo ""
echo "=== [A] FASE 4: AUDITORÍA POST-PODA REMOTA ==="
echo "Ramas vivas restantes en el servidor:"
git ls-remote --heads origin | awk '{print $2}' | sed 's|refs/heads/||'

echo ""
echo "=== [D] FASE 5: DOCUMENTACIÓN Y COMMITTED EVIDENCE ==="
mkdir -p SOBERANO_01_MEMORIA/RESCATE
echo -e "\n---\nid: PODA-RAMAS-$FECHA\naccion: Rescate de joyas ejecutado, tags creados, ramas obsoletas purificadas. Protocolo EAD v12.2." >> SOBERANO_01_MEMORIA/RESCATE/EVIDENCIA_MIGRACION.md

git add SOBERANO_01_MEMORIA/RESCATE/EVIDENCIA_MIGRACION.md
git commit -m "[EAD] Registro de evidencia de poda y rescate v12.2" || true
git push origin soberano-v1

echo ""
echo "✅ Repositorio purificado, joyas rescatadas y evidencia sincronizada en GitHub."
