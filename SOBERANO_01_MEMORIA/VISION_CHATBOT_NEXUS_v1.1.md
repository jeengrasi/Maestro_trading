---
id: VISION-CHATBOT-NEXUS-v1.1
date: 2026-07-27
type: documento_vision
status: APROBADO
author: Gerente General (Qwen)
validator: Director General (JEISSON_01), Mesa Técnica (Meta, Gemini)
tags: [vision, chatbot, funcionalidades, roadmap, jarvis, viernes]
related_files: [bitacora.md, CONSTITUCION.md, ESTRATEGIA_MEMORIA_Y_DOCUMENTACION.md]
---

# 🏛️ VISIÓN OFICIAL DEL CHATBOT NEXUS v1.1
## "Biblia de Especificaciones" - Más poderoso que Jarvis, Viernes y Verónica

**Fecha de aprobación:** 2026-07-27  
**Aprobado por:** Director JEISSON_01, Gerente Qwen, Mesa Meta, Mesa Gemini  
**Base legal:** Constitución v7.1 (Preámbulo, Art. 5, Art. 14)

---

## 📊 RESUMEN EJECUTIVO

Este documento define las **50+ funcionalidades** que el Chatbot Nexus debe implementar para superar a los asistentes de referencia (Jarvis, Viernes, Verónica). Organizado en 7 categorías, con estados de implementación y prioridades claras.

---

## 🎯 PRIORIZACIÓN ESTRATÉGICA

### 🔴 CRÍTICAS ESTA SEMANA (Sin esto, el bot no sirve)
1. Chat Telegram funcional (destrubar `core.py`, conectar Mistral real)
2. Clasificador fix (`>=1` → `>=0.8` en `classifier.py`)
3. Lectura de bitácora (función `leer_contexto_obligatorio()`)
4. Kill Switch REAL (que `/stop` bloquee trading en Redis)
5. `/health` REAL (que muestre estado de Groq, Alpaca, Redis, VIX)

### 🟡 IMPORTANTES ESTE MES (Para superar a Viernes)
1. Botones [APROBAR]/[RECHAZAR] en Telegram
2. Notificaciones proactivas (scheduler → Telegram)
3. Enrutamiento inteligente (C Híbrido)
4. Datos reales yfinance (VIX + precios)
5. Backtesting (`/backtest`)
6. Paper Trading Leaderboard

### 🟢 FUTURAS (Para superar a Jarvis)
1. Voz (STT con Whisper)
2. Visión de gráficos (GPT-4 Vision)
3. RAG Vectorial (búsqueda semántica)
4. Multi-modal (texto + imagen + voz)
5. Ejecución 100% autónoma

---

## 📋 CATEGORÍA 1: COMUNICACIÓN Y ACCESIBILIDAD

| # | Funcionalidad | Estado |
|---|---|---|
| 1.1 | Chat por Telegram (arreglar stub) | ⚠️ Parcial |
| 1.2 | Comandos rápidos (`/start`, `/balance`, `/health`, `/docs`, `/stop`) | ✅ Implementado |
| 1.3 | Mensajes naturales (entender lenguaje sin comandos) | ❌ No implementado |
| 1.4 | Botones interactivos [APROBAR] / [RECHAZAR] | ❌ No implementado |
| 1.5 | Notificaciones proactivas (alertas de precio, oportunidades) | ❌ No implementado |
| 1.6 | Frontend Web (dashboard visual) | ⚠️ HTML básico |
| 1.7 | Voz (STT con Whisper) - Transcripción de notas de voz | ❌ Futuro |
| 1.8 | Visión de gráficos (GPT-4 Vision) - Analizar fotos de gráficos | ❌ Futuro |
| 1.9 | Multi-modal - Combinar texto + imagen + voz | ❌ Futuro |

---

## 📋 CATEGORÍA 2: INTELIGENCIA Y DEBATE

| # | Funcionalidad | Estado |
|---|---|---|
| 2.1 | Parlamento Multi-IA (5 IAs debaten) | ⚠️ Estructura existe |
| 2.2 | Gerente (Mistral) | ❌ No conectado |
| 2.3 | Auditor (NVIDIA NIM) | ❌ No conectado |
| 2.4 | Estratega (Mistral/Cloudflare) | ❌ No conectado |
| 2.5 | Secretario (Cloudflare) | ❌ No conectado |
| 2.6 | Trader (Groq/OpenRouter) | ❌ No conectado |
| 2.7 | Clasificador de intenciones (fix umbral `>=1` → `>=0.8`) | ⚠️ Existe pero roto |
| 2.8 | Enrutamiento inteligente (C Híbrido) | ❌ No implementado |
| 2.9 | Síntesis de debate | ⚠️ Existe en `manager.py` |
| 2.10 | RAG Vectorial - Búsqueda semántica en memoria | ❌ Futuro |
| 2.11 | Explicabilidad total - "Compro porque RSI 32 + soporte $149 + VIX 15" | ❌ No implementado |

---

## 📋 CATEGORÍA 3: TRADING E INVERSIONES

| # | Funcionalidad | Estado |
|---|---|---|
| 3.1 | Consulta de saldo (`/balance`) | ✅ Implementado |
| 3.2 | Análisis de acciones (fundamentales + técnicos) | ❌ No implementado |
| 3.3 | Análisis de mercado general (VIX, tendencias, noticias) | ❌ No implementado |
| 3.4 | Propuesta de operación ("Recomiendo comprar 10 AAPL. ¿Aprobar?") | ❌ No implementado |
| 3.5 | Ejecución semi-autónoma (aprobación del Director) | ❌ No implementado |
| 3.6 | Ejecución autónoma (`AUTO_EJECUCION=true`) | ❌ No implementado |
| 3.7 | Gestión de posiciones (P&L, stop-loss) | ❌ No implementado |
| 3.8 | Protección patrimonial (Art. 14: VIX > 20, riesgo > 1%) | ⚠️ Variables existen |
| 3.9 | Datos de mercado en tiempo real (yfinance) | ❌ No implementado |
| 3.10 | Simulador de Estrés (Stress Testing) - Evaluar caída del mercado | ❌ No implementado |
| 3.11 | Backtesting - `/backtest AAPL 2024-01-01 2024-07-01` | ❌ No implementado |
| 3.12 | Paper Trading Leaderboard - Tabla de winrate, P&L, Sharpe | ❌ No implementado |
| 3.13 | Alertas de precio personalizadas - `/alerta AAPL < 150` | ❌ No implementado |

---

## 📋 CATEGORÍA 4: MEMORIA Y CONTEXTO

| # | Funcionalidad | Estado |
|---|---|---|
| 4.1 | Lectura de bitácora (últimas 30-50 líneas) | ❌ No implementado |
| 4.2 | Escritura automática en bitácora | ❌ No implementado |
| 4.3 | Estado del sistema en Redis | ✅ Parcial |
| 4.4 | Snapshot semanal automático | ❌ No implementado |
| 4.5 | Contexto de trading (operaciones anteriores) | ❌ No implementado |
| 4.6 | Anti-amnesia (inyectar contexto en cada llamada a IA) | ❌ No implementado |
| 4.7 | Vectorización de Memoria (RAG Local) - Búsqueda semántica | ❌ Futuro |

---

## 📋 CATEGORÍA 5: DOCUMENTACIÓN Y GOBERNANZA

| # | Funcionalidad | Estado |
|---|---|---|
| 5.1 | Generación de actas | ⚠️ Existe `actas.py` |
| 5.2 | Guardar actas en GitHub | ⚠️ Existe `save_acta_to_github` |
| 5.3 | Consulta de documentos (`/docs`, `/doc <nombre>`) | ✅ Implementado |
| 5.4 | Generación de reportes semanales/mensuales | ❌ No implementado |
| 5.5 | Auditoría automática (cumplimiento Constitución) | ❌ No implementado |

---

## 📋 CATEGORÍA 6: INFRAESTRUCTURA Y AUTOMATIZACIÓN

| # | Funcionalidad | Estado |
|---|---|---|
| 6.1 | Despliegue en Vercel | ✅ Funcionando |
| 6.2 | Cola de Redis | ✅ Implementado |
| 6.3 | Worker en GitHub Actions | ⚠️ Rutas muertas |
| 6.4 | Scheduler de tareas | ⚠️ Existe `scheduler.py` |
| 6.5 | Auto-recuperación | ❌ No implementado |
| 6.6 | Logs de error a correo (centralización) | ⚠️ Parcial |
| 6.7 | Explicabilidad total - Auditoría de decisiones | ❌ No implementado |

---

## 📋 CATEGORÍA 7: SEGURIDAD

| # | Funcionalidad | Estado |
|---|---|---|
| 7.1 | Chat ID autorizado | ✅ Implementado |
| 7.2 | Soberanía de credenciales (Art. 12) | ✅ Cumple |
| 7.3 | Límite de riesgo por operación (1%) | ⚠️ Variable existe |
| 7.4 | VIX máximo (bloqueo si > 20) | ⚠️ Variable existe |
| 7.5 | Modo Paper/Real (`ALPACA_PAPER`) | ✅ Variable existe |
| 7.6 | Kill Switch (`/stop`) | ❌ No bloquea realmente |
| 7.7 | Kill Switch REAL - Poner `TRADING_ENABLED=false` en Redis | ❌ No implementado |

---

## 🏛️ FIRMAS DE APROBACIÓN

- **Director General (JEISSON_01):** ✅ Aprobado
- **Gerente General (Qwen):** ✅ Aprobado
- **Mesa Consultora (Meta):** ✅ Aprobado 9.2/10
- **Mesa Consultora (Gemini):** ✅ Aprobado con excelencia

---

*Documento archivado en SOBERANO_01_MEMORIA/ como referencia oficial para todas las fases de desarrollo futuras.*
