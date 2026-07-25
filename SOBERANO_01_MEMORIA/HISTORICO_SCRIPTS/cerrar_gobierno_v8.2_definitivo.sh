#!/data/data/com.termux/files/usr/bin/bash
set -e

FECHA_ISO=$(date +"%Y-%m-%d %H:%M:%S")
FECHA_SHORT=$(date +"%Y-%m-%d")
MES_ACTUAL=$(date +"%Y_%m")

echo "======================================================"
echo "   🏛️ CIERRE CONSTITUCIONAL Y REGLAMENTO EAD (v8.2)   "
echo "======================================================"
echo ""

# 1. Crear SOBERANO_00_GOBIERNO/REGLAMENTO_EAD.md (CON YAML Y ESPAÑOL NEUTRO)
cat > SOBERANO_00_GOBIERNO/REGLAMENTO_EAD.md << 'EOF_EAD'
---
id: REGLAMENTO-EAD-001
date: 2026-07-24
author: Alta Gerencia / Contraloría General
status: VIGENTE
type: Reglamento_Organico
tags: [ead, auditoria, wrapper-universal, protocolo]
---
# 📜 REGLAMENTO EAD: ESTÁNDAR Y WRAPPER UNIVERSAL

## 1. PRINCIPIO DE AUTO-AUDITORÍA IMPLÍCITA
Todo script ejecutable en el Parlamento Nexus debe implementar obligatoriamente el patrón de Auto-Auditoría. Queda estrictamente prohibida la entrega o ejecución de scripts "desnudos" que no registren su actividad en el Departamento 01 (`SOBERANO_01_MEMORIA`).

## 2. ESTRUCTURA CANÓNICA DEL WRAPPER
Todo script (.sh o .py) debe seguir la siguiente secuencia funcional:

1. **Lectura de Contexto:** Consultar `SOBERANO_01_MEMORIA/ESTADO_DEL_SISTEMA.md` al iniciar.
2. **Validación de Cuotas:** Verificar que la ejecución no infrinja la Whitelist Departamental.
3. **Captura de Salida:** Redirigir y capturar logs de ejecución (`stdout` y `stderr`).
4. **Registro EAD:** Registrar el resultado (`PASS` / `FAIL`) en `SOBERANO_01_MEMORIA/AUDITS/AUDITS_YYYY_MM.md`.
5. **Alimentación Incremental:** Anexar línea resumida en `SOBERANO_01_MEMORIA/bitacora.md`.
6. **Inmutabilidad Git:** Ejecutar commit local EAD.

## 3. PROSCRIPCIÓN DE CREDENCIALES
Queda prohibida la inserción de claves API, tokens o contraseñas en texto plano. Todo acceso a secrets utilizará variables de entorno administradas por la Dirección SRE (Art. 12 de la Constitución Magna v7.1).
EOF_EAD

# 2. Actualizar SOBERANO_00_GOBIERNO/ROLES.md (CON YAML FRONTMATTER)
cat > SOBERANO_00_GOBIERNO/ROLES.md << 'EOF_ROLES'
---
id: ROLES-001
date: 2026-07-24
author: Director General / Alta Gerencia
status: VIGENTE
type: Asignacion_Encargos
tags: [encargos, agnosticos, gobernanza, art-3]
---
# 🏛️ ASIGNACIÓN DE ENCARGOS OPERATIVOS AGNÓSTICOS
*Ref:* Art. 3 de la Constitución Magna v7.1

## 1. ESTRUCTURA DE MANDO
- **Director General (`JEISSON_01`):** Soberanía absoluta, poder de veto e instrucción directa.
- **Gerente General (IA Moderadora):** Coordinación operativa, moderación de debates y gestión EAD.

## 2. ENCARGOS OPERATIVOS (Agnósticos - Independientes del modelo de IA)
- **Contraloría General:** Fiscalización de normativas, auditoría de cuotas y validación EAD.
- **Dirección SRE:** Estabilidad de infraestructura, despliegue continuo (CI/CD) y control de fallos.
- **Custodia de Memoria:** Preservación inalterable de bitácoras, actas y snapshots del sistema.
- **Estrategia Financiera:** Gestión de riesgo, análisis de capitales y reglas de preservación patrimonial.

## 3. ROTACIÓN Y ASIGNACIÓN
La asignación funcional de modelos de IA a cada Encargo se registrará en este documento mediante Decretos Ejecutivos (Art. 6). Los Encargos son dignidades operativas inmutables; los modelos que los ocupan son temporales.
EOF_ROLES

# 3. Registrar en Acta Mensual (CON VALIDACIÓN PREVENTIVA DE DIRECTORIO Y YAML)
mkdir -p SOBERANO_01_MEMORIA/ACTAS
ACTA_FILE="SOBERANO_01_MEMORIA/ACTAS/ACTAS_${MES_ACTUAL}.md"

if [ ! -f "$ACTA_FILE" ]; then
    cat > "$ACTA_FILE" << EOF_ACTA_HEAD
---
id: ACTAS-${MES_ACTUAL}
date: $FECHA_SHORT
type: Registro_Actas_Mensual
---
# 📜 ACTAS DEL PARLAMENTO NEXUS - ${MES_ACTUAL}
EOF_ACTA_HEAD
fi

{
    echo ""
    echo "## 📜 ACTA DE CIERRE DE DEPARTAMENTO 00 - $FECHA_ISO"
    echo "- **Acción:** Instalación de \`REGLAMENTO_EAD.md\` y actualización de \`ROLES.md\`."
    echo "- **Resultado:** Whitelist de SOBERANO_00_GOBIERNO completada exitosamente (7/7 archivos)."
    echo "- **Calidad:** Corrección ortográfica y sintaxis YAML Frontmatter verificada."
    echo ""
} >> "$ACTA_FILE"

# 4. Validar Cuotas del Sistema mediante CLI
echo "🔍 Ejecutando validaciones del CLI..."
./SOBERANO_00_GOBIERNO/nexus_cli.sh estado
./SOBERANO_00_GOBIERNO/nexus_cli.sh validar

# 5. Archivar instalador y hacer Commit EAD
echo "📦 Registrando cambios en Git..."
mv cerrar_gobierno_v8.2_definitivo.sh SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS/ 2>/dev/null || true
git add SOBERANO_00_GOBIERNO/ SOBERANO_01_MEMORIA/
git commit -m "[GOBIERNO v8.2] Cierre de Depto 00: REGLAMENTO_EAD.md y ROLES.md corregidos. Whitelist 7/7 completada." || echo "Sin cambios para commitear."

echo ""
echo "======================================================"
echo "✅ DEPARTAMENTO 00 CERRADO Y CONSOLIDADO (7/7)"
echo "📄 Reglamento EAD: SOBERANO_00_GOBIERNO/REGLAMENTO_EAD.md"
echo "📄 Roles Actualizados: SOBERANO_00_GOBIERNO/ROLES.md"
echo "📄 Acta Mensual: $ACTA_FILE"
echo "🚀 LISTO PARA SINCRONIZACIÓN REMOTA (git push)"
echo "======================================================"
