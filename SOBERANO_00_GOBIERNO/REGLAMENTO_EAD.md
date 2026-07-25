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
