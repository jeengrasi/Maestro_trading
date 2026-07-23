
# CONTEXTO COMPLETO DEL SISTEMA NEXUS IA
**GENERADO:** 2026-07-05T19:43:46-04:00
**SCRIPT:** SCR-CONTEXT-20260705-001
**DIRECTORIO BASE:** /data/data/com.termux/files/home/Maestro_trading
---

## 1. SISTEMA
**USUARIO:** u0_a287
**HOST:** localhost
**SO:** Linux localhost 4.14.186-27270957 #1 SMP PREEMPT Tue May 13 01:13:05 KST 2025 aarch64 Android
**UPTIME:** up 1 day, 6 hours, 8 minutes

### PROCESOS ACTIVOS
```
u0_a287  12075  0.0  0.0 2136816 3160 ?        S<    1970   0:02 runsv snx-ollama
u0_a287  12483  0.0  0.9 2371824 34568 ?       S<    1970   0:01 python3 /data/data/com.termux/files/home/soda/02-SISTEMA/BACKEND/snx_monitor_backend.py
u0_a287  15912  0.0  0.5 2282420 19972 ?       S<    1970   0:00 python3 -m http.server 8080 --directory /data/data/com.termux/files/home/soda/06-MONITOR/V3/
u0_a287  15917  0.0  0.0 2161400 3280 ?        S<    1970   0:00 svlogd -tt /data/data/com.termux/files/usr/var/log/snx-ollama
u0_a287  17087  0.0  0.8 3722500 31824 ?       S<l   1970   0:00 ollama serve
```

## 2. GIT Y GITHUB
**REPOSITORIO:** https://github.com/jeengrasi/Maestro_trading.git
**RAMA ACTUAL:** main

### ESTADO
```
?? 04-REGISTROS/DOCS/contexto_nexus_20260705_1943.md
```

### ULTIMOS 10 COMMITS
```
97ed461 feat: migrar backend a Railway (archivos de configuración)
1288a41 feat: implementar generador de Bitácora (plantilla + script Python + bitácora generada)
07215c0 Merge pull request #31 from jeengrasi/feature/actualizaciones-v2.0
d939b05 feat: actualizar actas.py e index.py a V2.0 (comandos /docs, /doc, /actas, Redis)
6e27045 Merge pull request #30 from jeengrasi/feature/redistribucion
5078640 feat: redistribuir archivos en departamentos (NADA SE BORRÓ)
ad03b46 feat: agregar estructura de departamentos (NADA SE BORRÓ)
86c5e1b Merge pull request #29 from jeengrasi/develop
a34c425 feat: inicializar estructura de departamentos con .gitkeep
7e11eed Merge pull request #28 from jeengrasi/develop
```

### RAMAS REMOTAS
```
  origin/Estable
  origin/HEAD -> origin/main
  origin/Staging
  origin/develop
  origin/feature/actualizaciones-v2.0
  origin/feature/fase2-bitacora
  origin/feature/redistribucion
  origin/main
  origin/railway/code-change-frJoSO
```

## 3. SERVICIOS EN EJECUCIÓN
```
u0_a287  12075  0.0  0.0 2136816 3160 ?        S<    1970   0:02 runsv snx-ollama
u0_a287  12483  0.0  0.9 2371824 34568 ?       S<    1970   0:01 python3 /data/data/com.termux/files/home/soda/02-SISTEMA/BACKEND/snx_monitor_backend.py
u0_a287  15912  0.0  0.5 2282420 19972 ?       S<    1970   0:00 python3 -m http.server 8080 --directory /data/data/com.termux/files/home/soda/06-MONITOR/V3/
u0_a287  15917  0.0  0.0 2161400 3280 ?        S<    1970   0:00 svlogd -tt /data/data/com.termux/files/usr/var/log/snx-ollama
u0_a287  17087  0.0  0.8 3722500 31824 ?       S<l   1970   0:00 ollama serve
```

## 4. REDIS (UPSTASH)
**URL:** https://relaxed-polecat-70802.upstash.io

### PING
{
  "result": "PONG"
}
### CLAVES RELEVANTES
```
{
  "result": null
}
{
  "result": null
}
```

## 5. ALPACA
**MODO:** REAL

### CUENTA
{
  "equity": "107893.55",
  "buying_power": "402912.37",
  "cash": "84270.99",
  "daytrade_count": 0
}
### POSICIONES ABIERTAS
{
  "symbol": "AAPL",
  "qty": "74",
  "market_value": "22838.62"
}
{
  "symbol": "MSFT",
  "qty": "1",
  "market_value": "390.49"
}
{
  "symbol": "TSLA",
  "qty": "1",
  "market_value": "393.45"
}

## 6. ESTRUCTURA DE DIRECTORIOS
### DIRECTORIOS PRINCIPALES
```
00-GOBIERNO
01-MEMORIA
02-SISTEMA
03-OPERACIONES
04-REGISTROS
05-DOCUMENTACION
06-MONITOR
Procfile
docs
railway.json
requirements.txt
runtime.txt
temp_departamentos.md
```

### ARBOL SIMPLIFICADO
```
/data/data/com.termux/files/home/Maestro_trading
.git
.git/hooks
.git/info
.git/objects
.git/objects/pack
.git/objects/info
.git/objects/51
.git/objects/22
.git/objects/5a
.git/objects/e6
.git/objects/d5
.git/objects/cc
.git/objects/a3
.git/objects/86
.git/objects/06
.git/objects/b7
.git/objects/11
.git/objects/20
.git/objects/4c
.git/objects/7c
.git/objects/7a
.git/objects/ae
.git/objects/fc
.git/objects/81
.git/objects/9b
.git/objects/ac
.git/objects/33
.git/objects/b5
.git/objects/47
```

## 7. DOCUMENTOS CLAVE
### CONSTITUCION (PRIMERAS 40 LINEAS)
# CONSTITUCIÓN DEL PARLAMENTO NEXUS

**Versión:** 4.0 | **Fecha:** 2026-06-23 | **Estado:** Vigente

---

## PREÁMBULO
El Parlamento Nexus es un ecosistema autónomo de IAs y humanos diseñado para generar ingresos financieros sin capital inicial, sin ventas ni freelance. Su fin último es la libertad financiera operativa del Director.

## CAPÍTULO I: PRINCIPIOS FUNDAMENTALES
- **Art. 1 (Soberanía):** El Director es la autoridad única. Ninguna IA prevalece sobre su voluntad.
- **Art. 2 (Transparencia):** Todo acto de gobierno es público, trazable y auditable.
- **Art. 3 (Resiliencia):** La preservación y crecimiento del patrimonio es el fin último. La seguridad es prioritaria sobre la ganancia especulativa.
- **Art. 4 (Agilidad):** La burocracia es enemiga del progreso. Se delega toda ejecución técnica a los Reglamentos Delegados.

## CAPÍTULO II: ESTRUCTURA Y DELEGACIÓN
- **Art. 5 (El Director):** Autoridad suprema. Modera, consulta y resuelve.
- **Art. 6 (La Mesa):** Cuerpo consultivo. Sus miembros son DeepSeek (Gerente), NotebookLM (Guardián), Copilot (Consultor Técnico) y Gemini (Consultor Estratégico).
- **Art. 7 (Independencia de Criterio):** Cada IA debe presentar su postura de forma independiente. El silencio no es validación. Prohibido el sesgo de cortesía.

## CAPÍTULO III: SEGURIDAD Y VETO
- **Art. 8 (Veto en Caliente):** El Director posee derecho de veto absoluto, ejecutable en menos de 1 segundo.
- **Art. 9 (Salvaguarda Automática):** El sistema debe contar con mecanismos de autoprotección contra riesgos catastróficos.

## CAPÍTULO IV: GOBERNANZA DOCUMENTAL
- **Art. 10 (Soberanía Documental):** Solo lo indexado en NotebookLM tiene validez.
- **Art. 11 (Trazabilidad):** Toda decisión debe serializarse en Markdown.
- **Art. 12 (Justificación Evidencial):** Si una IA contradice una directriz, debe justificarlo con evidencia documentada.

## CAPÍTULO V: REFORMA
- **Art. 13 (Enmienda):** Reforma requiere propuesta formal, debate de Mesa y ratificación del Director.

## CAPÍTULO VI: FASES DEL PROYECTO
| Fase | Nombre | Objetivo | Estado |
| :--- | :--- | :--- | :--- |
| Fase 0 | Cimentación | Gobernanza, roles, documentación. | Cerrada |
| Fase 1 | Estabilización | Auditoría, secretos, reactivación del bot. | En curso |
| Fase 2 | Seguridad y Comunicación | Chat Parlamentario, breakers, logs. | Pendiente |
| Fase 3 | Operación y Monitoreo | Ejecución en vivo y optimización. | Pendiente |

### BITACORA (PRIMERAS 60 LINEAS)
# BITÁCORA GLOBAL DE NEXUS IA

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
---

## 1. IDENTIDAD DEL PROYECTO

| Campo | Valor |
|-------|-------|
| **Nombre del Sistema** | Maestro Nexus AI |
| **Alias** | Nexus / Jarvis Financiero |
| **Versión Actual** | 2.1 |
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

## 8. VARIABLES DE ENTORNO
- UPSTASH_REDIS_REST_URL: CONFIGURADA (longitud: 22)
- UPSTASH_REDIS_REST_TOKEN: CONFIGURADA (longitud: 24)
- ALPACA_API_KEY: CONFIGURADA (longitud: 14)
- ALPACA_SECRET_KEY: CONFIGURADA (longitud: 17)
- ALPACA_PAPER: NO CONFIGURADA
- MISTRAL_API_KEY: CONFIGURADA (longitud: 15)
- GITHUB_TOKEN: CONFIGURADA (longitud: 12)
- NVIDIA_NIM_API_KEY: CONFIGURADA (longitud: 18)
- AION_API_KEY: CONFIGURADA (longitud: 12)
- CLOUDFLARE_API_TOKEN: CONFIGURADA (longitud: 20)
- CLOUDFLARE_ACCOUNT_ID: CONFIGURADA (longitud: 21)

## 9. HEALTH CHECKS
### BACKEND LOCAL
```
HTTP 000 en 0.000000s
No responde
```

### BACKEND REMOTO (VERCEL)
```
HTTP 500 en 3.468711s
```

## 10. ULTIMOS 5 COMMITS
```
97ed461 feat: migrar backend a Railway (archivos de configuración)
1288a41 feat: implementar generador de Bitácora (plantilla + script Python + bitácora generada)
07215c0 Merge pull request #31 from jeengrasi/feature/actualizaciones-v2.0
d939b05 feat: actualizar actas.py e index.py a V2.0 (comandos /docs, /doc, /actas, Redis)
6e27045 Merge pull request #30 from jeengrasi/feature/redistribucion
```

---
## 11. RESUMEN EJECUTIVO
- **SISTEMA:** Linux localhost 4.14.186-27270957 #1 SMP PREEMPT Tue May 13 01:13:05 KST 2025 aarch64 Android
- **REPOSITORIO:** https://github.com/jeengrasi/Maestro_trading.git
- **RAMA:** main
- **ULTIMO COMMIT:** 97ed461 feat: migrar backend a Railway (archivos de configuración)
- **ALPACA:** REAL
- **REDIS:** CONFIGURADO
- **BACKEND LOCAL:** 000NO RESPONDE

**CUALQUIER IA QUE LEA ESTE ARCHIVO PUEDE RECONSTRUIR EL CONTEXTO COMPLETO DEL SISTEMA NEXUS IA.**

