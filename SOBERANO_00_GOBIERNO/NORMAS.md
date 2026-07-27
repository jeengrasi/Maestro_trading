---
id: NORMAS-SISTEMA-NEXUS
date: 2026-07-27
type: documento_normativo
status: VIGENTE
author: Gerente General (Qwen)
validator: Director General (JEISSON_01), Mesa Tecnica (Meta, Gemini)
tags: [normas, edvc, documentacion, trazabilidad, codigo, memoria]
related_files: [CONSTITUCION.md, bitacora.md]
---

# NORMAS DEL SISTEMA NEXUS

**Estado:** VIGENTE  
**Ultima actualizacion:** 2026-07-27  
**Base legal:** Constitucion v7.1 (Art. 9 Anticaos, Art. 11 Protocolo EAD)

---

## NORMA 1: EDVC v1.0 - Estandar de Documentacion Viva en Codigo

**Estado:** OBLIGATORIO  
**Aplicacion:** Todo el repositorio  
**Fecha de aprobacion:** 2026-07-27

### 1.1 PRINCIPIO FUNDAMENTAL

El codigo no es solo instrucciones para la maquina; es la **memoria escrita del sistema**. Todo archivo .py debe ser autodocumentado, trazable y comprensible en menos de 60 segundos.

### 1.2 LAS 4 CAPAS OBLIGATORIAS

#### CAPA 1: Cedula de Identidad (Encabezado)

Ejemplo de formato:

    # ==============================================================================
    # ARCHIVO: [nombre_archivo.py]
    # SISTEMA: MAESTRO-NEXUS
    # PROPOSITO: [Descripcion de 1-2 lineas]
    # ULTIMA MODIFICACION MAYOR: [YYYY-MM-DD]
    # AUTOR: [Nombre/Rol] | VALIDADO POR: [Nombre/Rol]
    # DOCUMENTO DE AUDITORIA: [Ruta al archivo .md en AUDITS/]
    # ==============================================================================

#### CAPA 2: Contexto de Seccion

Antes de bloques logicos grandes, explicar el PORQUE arquitectonico.

Ejemplo:

    # ================================================
    # SECCION X: [NOMBRE]
    # ================================================
    # [CONTEXTO ARQUITECTONICO]
    # MOTIVO: Explicacion de por que se eligio esta logica.
    # SOLUCION: Como se resolvio el problema.
    # ================================================

#### CAPA 3: La Cicatriz Quirurgica (Modificaciones Criticas)

Cualquier cambio critico DEBE llevar esta etiqueta:

    # [MOD-YYYY-MM-DD] [AUTOR: X] [VALIDADOR: Y]
    # MOTIVO: [Razon especifica del cambio]
    # REF: [Referencia a log, issue o auditoria]

#### CAPA 4: Changelog Vivo (Pie de archivo)

Registro cronologico inverso al final del archivo:

    # ==============================================================================
    # REGISTRO DE CAMBIOS (CHANGELOG VIVO)
    # ==============================================================================
    # [YYYY-MM-DD] [Autor]: Descripcion del cambio (Ref: AUDIT-XXXX)
    # ==============================================================================

### 1.3 PROHIBICIONES (Art. 9 Anticaos)

- NO comentar cada linea individual (genera ruido visual).
- NO dejar codigo comentado sin etiqueta [DEPRECATED-YYYY-MM-DD].
- NO modificar logica critica sin anadir la Capa 3.
- NO crear archivos sin la Capa 1.

### 1.4 INTEGRACION EN EL CHATBOT

El System Prompt de todos los roles del Parlamento DEBE incluir:

    INSTRUCCION CRITICA (NORMA EDVC v1.0):
    Cada vez que generes o modifiques codigo, DEBES aplicar las 4 capas del estandar EDVC.
    Si no cumples, tu respuesta sera rechazada por el Auditor de Riesgos.

### 1.5 AUDITORIA DE CUMPLIMIENTO

Cada archivo debe apuntar a un documento de auditoria en SOBERANO_01_MEMORIA/AUDITS/ que detalle:
- Que se cambio
- Por que se cambio
- Quien lo aprobo
- Cuando se aplico

---

## NORMA 2: [Proxima Norma a Definir]

*Espacio reservado para futuras normas del sistema.*

---

*Este documento es vinculante para todo el sistema Nexus.*
