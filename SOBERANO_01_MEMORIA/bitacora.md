# BITÁCORA MAESTRO NEXUS
**Sistema Autónomo de Gestión Financiera y Parlamento de IAs**

<<<<<<< HEAD
=======
<<<<<<< Updated upstream
## 2026
- **2026-04-17** | FUNDACIÓN | Proyecto Nexus IA fundado. | DeepSeek
- **2026-06-14** | CONSTITUCIÓN V.3.1 | Ratificación del marco de gobernanza. | Director
- **2026-06-17** | NUEVA GERENCIA | DeepSeek asume como Gerente General. Cierre Fase 0. | DeepSeek
- **2026-06-24** | BOT REACTIVADO | Bot responde. Error de await corregido. | DeepSeek
- **2026-06-24** | CHAT RATIFICADO | NEXUS-PROY-001 aprobado. | Director
- **2026-06-25** | ROUTER RATIFICADO | Router.py v1.3 con telemetría. | DeepSeek
- **2026-06-28** | PARLAMENTO ACTIVADO | 4 roles funcionando. | DeepSeek
- **2026-06-29** | TERMUX INTEGRADO | Scripts de control. | DeepSeek
- **2026-06-30** | MODULARIZACIÓN | Código separado en módulos. | DeepSeek
- **2026-06-30** | DOCUMENTOS EN GITHUB | Migración desde Drive. | DeepSeek
=======
>>>>>>> 1288a41 (feat: implementar generador de Bitácora (plantilla + script Python + bitácora generada))
---

## 1. IDENTIDAD DEL PROYECTO

| Campo | Valor |
|-------|-------|
| **Nombre del Sistema** | Maestro Nexus AI |
| **Alias** | Nexus / Jarvis Financiero |
<<<<<<< HEAD
| **Versión Actual** | V2.1 (Scheduler Activo) |
=======
| **Versión Actual** | 2.1 |
>>>>>>> 1288a41 (feat: implementar generador de Bitácora (plantilla + script Python + bitácora generada))
| **Fecha de Fundación** | 2026-06-23 |
| **Director** | JEISSON_01 |
| **Propósito** | Lograr la libertad financiera del Director mediante un sistema autónomo de trading, inversión y gestión documental impulsado por un parlamento de IAs. |

---

## 2. MISIÓN, VISIÓN Y VALORES

### Misión
Construir un ecosistema de inteligencia artificial autónomo que gestione, invierta y documente decisiones financieras con la precisión de un comité de expertos, operando 24/7 sin intervención humana.

### Visión
Ser el primer 'Director Financiero Digital' del mundo, capaz de superar a los fondos de inversión tradicionales mediante la sinergia de múltiples IAs, memoria perpetua y automejora continua.

### Valores Operativos
1. **Soberanía del Director:** El humano tiene veto absoluto.
2. **Transparencia Radical:** Toda decisión queda documentada en actas trazables.
3. **Resiliencia:** El sistema debe proteger el capital por encima de la especulación.
4. **Agilidad:** La burocracia es enemiga del progreso; se delega en scripts.

---

## 3. ARQUITECTURA GENERAL

### Capas del Sistema

| Capa | Componente | Tecnología | Propósito |
|------|------------|------------|-----------|
| **Interfaz** | Telegram Bot | Python / Telegram API | Comunicación con el usuario |
| **Núcleo** | FastAPI Server | Python / Uvicorn | Gestión de webhooks y lógica interna |
| **Cerebro** | Parlamento de IAs | Mistral, Llama, Groq, OpenRouter | Debate y toma de decisiones |
| **Memoria Rápida** | Redis Cache | Upstash Redis | Contexto de sesión (24h) |
| **Memoria Institucional** | GitHub Repo | Markdown / JSON | Actas, documentos y versionado |
| **Broker** | Alpaca API | Python SDK | Ejecución de operaciones en papel |
| **Scheduler** | Motor Interno | asyncio / Python | Tareas autónomas programadas |

<<<<<<< HEAD
### Flujo de Datos
1. **Usuario escribe** en Telegram -> Webhook.
2. **Clasificador** detecta intención (Mercado, Auditoría, Documentación, General).
3. **Si es financiero:** Debate parlamentario (Auditor, Estratega, Guardián).
4. **Gerente** emite recomendación final.
5. **Se genera acta** en GitHub y se indexa en Redis.
6. **El Scheduler** ejecuta tareas de fondo (health check, limpieza).

---

## 4. ESTRUCTURA DE DEPARTAMENTOS (REPOSITORIO)

```
Maestro_trading/
├── 00-GOBIERNO/                 # Gobernanza y roles
│   └── DOCS/
│       ├── NEXUS_MANIFEST.json  # Constitución del sistema
│       ├── constitucion.md      # Normas fundamentales
│       ├── roles.md             # Descripción de cada IA
│       └── seguridad/           # Políticas de seguridad
├── 01-MEMORIA/                  # Memoria persistente
│   ├── API/                     # Conexión con Redis
│   ├── DOCS/
│   │   └── actas/               # Todas las actas generadas
│   └── SCRIPTS/                 # Scripts de indexación
├── 02-SISTEMA/                  # Código y lógica
│   ├── API/
│   │   ├── api/
│   │   │   ├── core/            # Scheduler y utilidades
│   │   │   ├── parliament/      # Lógica de debate
│   │   │   ├── memory/          # Bootstrap de Redis
│   │   │   ├── providers/       # Conectores a IAs
│   │   │   ├── telegram/        # Utilidades de envío
│   │   │   ├── config.py        # Variables de entorno
│   │   │   ├── index.py         # Punto de entrada
│   │   │   └── router.py        # Enrutamiento de mensajes
│   ├── DOCS/                    # Documentación técnica
│   └── LAYERS/                  # Capas (ChatOps, Telecom)
├── 03-OPERACIONES/              # Trading y ejecución
│   └── ENGINE/
│       └── main.py              # Motor de fondo (queue)
├── 04-REGISTROS/                # Logs y auditoría
│   └── DOCS/
│       ├── bitacora.md          # Este documento
│       └── bloque_actas.txt     # Historial de actas
├── 05-DOCUMENTACION/            # Archivo central
│   └── DOCS/
│       ├── 00_INDICE.md
│       └── README.md
└── 06-MONITOR/                  # Monitoreo y salud
    └── DOCS/                    # Dashboards y health checks
=======
---

## 4. ESTRUCTURA DE DEPARTAMENTOS

```
Maestro_trading/
├── 00-GOBIERNO/
│   └── DOCS/
│       ├── NEXUS_MANIFEST.json
│       ├── constitucion.md
│       ├── roles.md
│       └── seguridad/
├── 01-MEMORIA/
│   ├── API/
│   ├── DOCS/
│   │   └── actas/
│   └── SCRIPTS/
├── 02-SISTEMA/
│   ├── API/
│   │   └── api/
│   │       ├── core/
│   │       ├── parliament/
│   │       ├── memory/
│   │       ├── providers/
│   │       └── telegram/
│   ├── DOCS/
│   └── LAYERS/
├── 03-OPERACIONES/
│   └── ENGINE/
│       └── main.py
├── 04-REGISTROS/
│   └── DOCS/
│       ├── bitacora.md
│       └── bloque_actas.txt
├── 05-DOCUMENTACION/
│   └── DOCS/
│       ├── 00_INDICE.md
│       └── README.md
└── 06-MONITOR/
    └── DOCS/
>>>>>>> 1288a41 (feat: implementar generador de Bitácora (plantilla + script Python + bitácora generada))
```

---

## 5. HERRAMIENTAS Y PROVEEDORES IA

### Servicios Activos

| Herramienta | Uso | Estado |
|-------------|-----|--------|
| **GitHub** | Repositorio y almacenamiento de actas | ✅ Activo |
| **Vercel** | Hosting de la API (FastAPI) | ✅ Activo |
| **Railway** | Backend alternativo (webhook) | ⚠️ Con errores |
| **Upstash Redis** | Memoria rápida (contexto, caché) | ✅ Activo |
| **Alpaca** | Broker de trading (paper) | ✅ Activo |
| **Telegram** | Interfaz de usuario | ✅ Activo |
| **Termux** | Entorno de desarrollo y control | ✅ Activo |

<<<<<<< HEAD
### Proveedores IA (Parlamento)

| IA | Rol | Proveedor | Modelo | Propósito |
|----|-----|-----------|--------|-----------|
| **Gerente** | DeepSeek | Mistral | mistral-small | Decisión final, estrategia |
| **Auditor** | Meta-Llama | NVIDIA | meta/llama-3.1-8b-instruct | Validación técnica y riesgos |
| **Estratega** | Gemini | Mistral | mistral-small | Análisis financiero y de mercado |
| **Guardián** | Copilot | GitHub | gpt-4o-mini | Memoria documental y trazabilidad |
| **Secretario** | Cloudflare | Cloudflare | @cf/meta/llama-3.1-8b-instruct | Generación de actas |

=======
>>>>>>> 1288a41 (feat: implementar generador de Bitácora (plantilla + script Python + bitácora generada))
---

## 6. CARTERA DE COMANDOS TELEGRAM

| Comando | Función | Estado |
|---------|---------|--------|
<<<<<<< HEAD
| `/start` | Mostrar estado del bot y comandos disponibles | ✅ |
| `/docs` | Listar documentos indexados en Redis | ✅ |
| `/doc <nombre>` | Consultar contenido de un documento | ✅ |
| `/actas` | Listar actas generadas por el parlamento | ✅ |
| `/balance` | Consultar saldo de Alpaca (paper trading) | ✅ |
| `/chatid` | Obtener ID del chat autorizado | ✅ |
| `/stop` | Pausar el sistema (emergencia) | ✅ |
| `/scheduler` | Ver estado del motor de tareas | ✅ |
| `/health` | Verificar estado de los servicios | ✅ |
| `Mensaje natural` | Clasifica automáticamente y debate | ✅ |

---

## 7. PLAN DE EVOLUCIÓN (PRIORIDADES APROBADAS)

| # | Prioridad | Descripción | Plazo |
|---|-----------|-------------|-------|
| 1 | **Scheduler Interno** | Motor de tareas autónomas (health check, limpieza) | ✅ IMPLEMENTADO |
| 2 | **Memoria Vectorial** | Base de datos con embeddings para búsqueda semántica | 2 semanas |
| 3 | **Auto‑reparación** | Health checks completos y alertas automáticas | 1 semana |
| 4 | **Base de Conocimiento** | Documentación estructurada del sistema | 2 semanas |
| 5 | **Rate Limiting** | Control de abusos y auditoría de usuarios | 1 semana |

---

## 8. NORMAS Y CONSTITUCIÓN (EXTRACTO)

*(Para consulta completa, ver `00-GOBIERNO/DOCS/constitucion.md`)*
=======
| `/start` | Mostrar estado del bot | ✅ |
| `/docs` | Listar documentos indexados | ✅ |
| `/doc <nombre>` | Consultar documento | ✅ |
| `/actas` | Listar actas | ✅ |
| `/balance` | Ver saldo Alpaca | ✅ |
| `/chatid` | Ver ID del chat | ✅ |
| `/stop` | Pausar el sistema | ✅ |
| `/scheduler` | Estado del scheduler | ✅ |
| `/health` | Estado de servicios | ✅ |

---

## 7. PLAN DE EVOLUCIÓN

| # | Prioridad | Descripción | Plazo |
|---|-----------|-------------|-------|
| 1 | **Scheduler Interno** | Tareas autónomas | ✅ IMPLEMENTADO |
| 2 | **Memoria Vectorial** | Búsqueda semántica | 2 semanas |
| 3 | **Auto‑reparación** | Health checks | 1 semana |
| 4 | **Base de Conocimiento** | Documentación estructurada | 2 semanas |
| 5 | **Rate Limiting** | Control de abusos | 1 semana |

---

## 8. NORMAS Y CONSTITUCIÓN
>>>>>>> 1288a41 (feat: implementar generador de Bitácora (plantilla + script Python + bitácora generada))

- **Art. 1 (Soberanía):** El Director es la autoridad única.
- **Art. 6 (La Mesa):** Cuerpo consultivo compuesto por DeepSeek, Copilot y Gemini.
- **Art. 10 (Soberanía Documental):** Solo lo indexado en el sistema tiene validez.
- **Art. 13 (Reforma):** Cambios requieren propuesta formal y debate de Mesa.

---

<<<<<<< HEAD
## 9. BITÁCORA DE CAMBIOS (EVOLUCIÓN DEL SISTEMA)
=======
## 9. BITÁCORA DE CAMBIOS
>>>>>>> 1288a41 (feat: implementar generador de Bitácora (plantilla + script Python + bitácora generada))

| Fecha | Versión | Cambio | Responsable |
|-------|---------|--------|-------------|
| 2026-06-23 | v1.0 | Fundación del Parlamento Nexus | JEISSON_01 |
<<<<<<< HEAD
| 2026-06-30 | v1.7 | Memoria en 3 niveles (Redis, GitHub) | Gerente |
| 2026-07-04 | v2.0 | Comandos /docs, /doc, /actas | Gerente |
| 2026-07-04 | v2.1 | Scheduler interno (tareas autónomas) | Gerente + CTO |
=======
| 2026-06-30 | v1.7 | Memoria en 3 niveles | Gerente |
| 2026-07-04 | v2.0 | Comandos /docs, /doc, /actas | Gerente |
| 2026-07-04 | v2.1 | Scheduler interno | Gerente + CTO |
>>>>>>> 1288a41 (feat: implementar generador de Bitácora (plantilla + script Python + bitácora generada))

---

## 10. REFERENCIAS Y ENLACES

- **Repositorio:** https://github.com/jeengrasi/Maestro_trading
- **Vercel (API):** https://maestro-trading.vercel.app
- **Actas en GitHub:** https://github.com/jeengrasi/Maestro_trading/tree/main/01-MEMORIA/DOCS/actas
- **Constitución:** https://github.com/jeengrasi/Maestro_trading/blob/main/00-GOBIERNO/DOCS/constitucion.md

---

**Última actualización:** 2026-07-04
**Elaborado por:** Gerente (DeepSeek)
**Validado por:** Mesa Parlamentaria (Gemini, Copilot)
**Aprobado por:** Director JEISSON_01
<<<<<<< HEAD
=======
>>>>>>> Stashed changes
>>>>>>> 1288a41 (feat: implementar generador de Bitácora (plantilla + script Python + bitácora generada))
[2026-07-24 18:51:45] [EAD] Promulgación e instalación de Constitución Magna v7.1 en SOBERANO_00_GOBIERNO/CONSTITUCION.md (v4.0 eliminada, worker.yml relocalizado)
[2026-07-24 23:14:26] [INSPECCION] Auditoría EAD de SOBERANO_02_CORE completada via nexus_cli.sh.
[2026-07-24 23:42:48] [VEEDURIA PASS] SOBERANO_02_CORE/core/scheduler.py supero los 5 filtros en 0ms.
[2026-07-24 23:44:53] [VEEDURIA PASS] SOBERANO_02_CORE/core/generar_bitacora.py supero los 5 filtros en 0ms.
[2026-07-24 23:48:24] [VEEDURIA PASS] SOBERANO_02_CORE/core/scheduler.py supero los 5 filtros en 0ms.
[2026-07-24 23:50:35] [VEEDURIA PASS] SOBERANO_02_CORE/core/generar_bitacora.py supero los 5 filtros en 0ms.
[2026-07-24 23:58:48] [VEEDURIA PASS] SOBERANO_03_NEXUS/nexus_bridge.py supero los 5 filtros en 0ms.
[2026-07-24 23:59:34] [INFO] [NEXUS_BRIDGE] Iniciando escaneo dinámico de conectores y APIs...
[2026-07-24 23:59:34] [WARN] [NEXUS_BRIDGE] No se detectaron variables de API en el entorno local.
[2026-07-25 00:14:09] [INSPECCION] Auditoría de lógica de motor, bot e índices completada.
[2026-07-25 07:42:25] [VEEDURIA PASS] SOBERANO_03_NEXUS/rastrear_rutas_ead.py supero los 5 filtros en 0ms.
[2026-07-25 07:42:27] [PASS] [RASTREO_EAD] Rastreos encontrados: 16 líneas de importación.
[2026-07-25 08:21:55] [VEEDURIA PASS] SOBERANO_03_NEXUS/index.py supero los 5 filtros en 0ms.
[2026-07-25 08:21:58] [VEEDURIA PASS] SOBERANO_03_NEXUS/router.py supero los 5 filtros en 0ms.
[2026-07-25 08:21:59] [PASS] [RASTREO_EAD] Rastreos encontrados: 16 líneas de importación.
[2026-07-25 22:44:37] [VEEDURIA PASS] SOBERANO_03_NEXUS/index.py superó los 5 filtros + Constitución en 0ms.
[2026-07-25 22:46:04] [VEEDURIA PASS] SOBERANO_03_NEXUS/index.py superó los 5 filtros + Constitución en 0ms.
[2026-07-25 22:46:55] [VEEDURIA PASS] SOBERANO_03_NEXUS/index.py superó los 5 filtros + Constitución en 0ms.
[2026-07-25 22:47:23] [VEEDURIA PASS] SOBERANO_03_NEXUS/index.py superó los 5 filtros + Constitución en 0ms.

- **2026-07-26** | **HITO ESTRATÉGICO** | **Visión Oficial del Chatbot Nexus v1.1 definida y aprobada**.
  - Documento: 
  - Contenido: 50+ funcionalidades en 7 categorías, con estados y prioridades.
  - Aprobado por: Director JEISSON_01, Gerente Qwen, Mesa Meta, Mesa Gemini.
  - Prioridad #1: Destrubar stubs y conectar IA real (Mistral) para chat funcional.
  - Próximo paso: Implementar funcionalidades críticas de esta semana.
  - Autor: Gerente General (Qwen) | Validado por: Mesa Técnica

- **2026-07-27 15:08:17** | **HITO ESTRATEGICO** | Cierre oficial de Fases 1 y 2. Documento de Resumen y Hoja de Ruta (Fases 3-5) archivado en MEMORIA. Sistema 100% operativo, resiliente y bajo Norma EDVC v1.0.
