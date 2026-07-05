# BITÁCORA MAESTRO NEXUS
**Sistema Autónomo de Gestión Financiera y Parlamento de IAs**

---

## 1. IDENTIDAD DEL PROYECTO

| Campo | Valor |
|-------|-------|
| **Nombre del Sistema** | Maestro Nexus AI |
| **Alias** | Nexus / Jarvis Financiero |
| **Versión Actual** | V2.1 (Scheduler Activo) |
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

### Proveedores IA (Parlamento)

| IA | Rol | Proveedor | Modelo | Propósito |
|----|-----|-----------|--------|-----------|
| **Gerente** | DeepSeek | Mistral | mistral-small | Decisión final, estrategia |
| **Auditor** | Meta-Llama | NVIDIA | meta/llama-3.1-8b-instruct | Validación técnica y riesgos |
| **Estratega** | Gemini | Mistral | mistral-small | Análisis financiero y de mercado |
| **Guardián** | Copilot | GitHub | gpt-4o-mini | Memoria documental y trazabilidad |
| **Secretario** | Cloudflare | Cloudflare | @cf/meta/llama-3.1-8b-instruct | Generación de actas |

---

## 6. CARTERA DE COMANDOS TELEGRAM

| Comando | Función | Estado |
|---------|---------|--------|
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

- **Art. 1 (Soberanía):** El Director es la autoridad única.
- **Art. 6 (La Mesa):** Cuerpo consultivo compuesto por DeepSeek, Copilot y Gemini.
- **Art. 10 (Soberanía Documental):** Solo lo indexado en el sistema tiene validez.
- **Art. 13 (Reforma):** Cambios requieren propuesta formal y debate de Mesa.

---

## 9. BITÁCORA DE CAMBIOS (EVOLUCIÓN DEL SISTEMA)

| Fecha | Versión | Cambio | Responsable |
|-------|---------|--------|-------------|
| 2026-06-23 | v1.0 | Fundación del Parlamento Nexus | JEISSON_01 |
| 2026-06-30 | v1.7 | Memoria en 3 niveles (Redis, GitHub) | Gerente |
| 2026-07-04 | v2.0 | Comandos /docs, /doc, /actas | Gerente |
| 2026-07-04 | v2.1 | Scheduler interno (tareas autónomas) | Gerente + CTO |

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
