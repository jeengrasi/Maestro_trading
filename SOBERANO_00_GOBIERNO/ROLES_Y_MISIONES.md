# 🏛️ MANIFIESTO DE ROLES Y MISIONES DEL SISTEMA MAESTRO-NEXUS

**Versión:** 1.0  
**Fecha de creación:** 2026-07-30  
**Autor:** Gerente Qwen | **Validador:** Director JEISSON_01  
**Referencia:** Constitución v7.1 (Art. 5, 9, 11, 12, 14)  
**Estado:** ✅ APROBADO

---

## 📜 PROPÓSITO DEL DOCUMENTO

Este manifiesto define la **estructura jerárquica inmutable** del sistema Maestro-Nexus. Cada script del proyecto tiene asignado un **Departamento**, un **Rol**, una **Misión**, unos **Deberes** y unas **Prohibiciones**. 

**Principio rector (Art. 5):** *"La memoria es el sistema, no la memoria de la IA."*  
Los roles están escritos en este archivo, no en la mente volátil de Mistral. Si un script hace algo que no está en su misión, es una **violación constitucional**.

---

## 🗺️ MAPA DE DEPARTAMENTOS

| Código | Departamento | Propósito |
|--------|--------------|-----------|
| `00` | **GOBIERNO** | Auditoría, integridad y control constitucional |
| `01` | **MEMORIA** | Registro soberano de decisiones y trazabilidad |
| `03` | **NEXUS** | Núcleo operativo: cognición, trading, telecomunicaciones |

---

## 🏛️ DEPARTAMENTO 00: GOBIERNO

### 📋 Script Jefe: `core/contralor.py`
- **Rol:** El Veedor Supremo
- **Misión:** Auditar la integridad de los archivos de gobierno y bloquear ejecuciones no autorizadas.
- **Deberes:**
  1. Calcular hashes SHA-256 de archivos críticos.
  2. Comparar hashes contra valores esperados.
  3. Bloquear `AUTO_EJECUCION_TEMP` en Redis si detecta alteraciones.
  4. Generar reportes de integridad en formato EDVC.
- **Prohibiciones:**
  1. ❌ Ejecutar operaciones de trading.
  2. ❌ Enviar mensajes a Telegram.
  3. ❌ Modificar archivos de gobierno por sí mismo.

---

## 📚 DEPARTAMENTO 01: MEMORIA

### 📋 Script Jefe: `core/memory_logger.py`
- **Rol:** El Escribano Oficial
- **Misión:** Registrar todas las decisiones del sistema en la Bitácora Soberana (`bitacora.md`).
- **Deberes:**
  1. Escribir cada interacción con fecha, hora, chat_id y resumen.
  2. Si el entorno es de solo lectura (Vercel), hacer fallback a Redis con TTL 24h.
  3. Nunca colapsar silenciosamente ante errores de escritura.
  4. Cumplir formato EDVC en cada entrada.
- **Prohibiciones:**
  1. ❌ Tomar decisiones de trading.
  2. ❌ Modificar archivos de gobierno.
  3. ❌ Enviar mensajes a Telegram.

---

## ⚙️ DEPARTAMENTO 03: NEXUS

### 🧠 Sub-departamento 3.1: PARLAMENTO (Cognición)

#### 📋 Script Jefe: `parliament/core.py`
- **Rol:** El Cerebro Cognitivo
- **Misión:** Orquestar el Tool-Calling, aplicar reglas EDVC y mantener la ventana de contexto conversacional.
- **Deberes:**
  1. Gestionar memoria deslizante en Redis (últimos 4 mensajes, TTL 1h).
  2. Aplicar reglas de concisión ejecutiva (máx. 250 palabras, veredicto primero).
  3. Invocar herramientas vía Mistral con límite de 2 por turno.
  4. Rechazar respuestas sin datos duros (regla anti-alucinación).
- **Prohibiciones:**
  1. ❌ Ejecutar órdenes de trading directamente.
  2. ❌ Almacenar datos permanentemente en disco.

#### 📋 Script Jefe: `parliament/tool_caller.py`
- **Rol:** El Ejecutor de Herramientas
- **Misión:** Ejecutar herramientas externas (Alpaca, GitHub) y devolver resultados estructurados.
- **Deberes:**
  1. Usar `https://data.alpaca.markets` para datos de mercado (docs oficiales).
  2. Devolver mensajes de error claros con prefijo `[ERROR DE HERRAMIENTA]`.
  3. Aplicar `.strip()` a todas las credenciales de entorno.
- **Prohibiciones:**
  1. ❌ Reintentar herramientas fallidas más de 2 veces.
  2. ❌ Enviar mensajes a Telegram.
  3. ❌ Tomar decisiones de trading.

#### 📋 Script Jefe: `parliament/github_rag.py`
- **Rol:** El Bibliotecario RAG
- **Misión:** Consultar archivos de gobierno en GitHub cuando el usuario pregunta por normas.
- **Deberes:**
  1. Leer `CONSTITUCION.md` y `NORMAS.md` vía API de GitHub.
  2. Devolver contexto normativo estructurado.
- **Prohibiciones:**
  1. ❌ Modificar archivos de gobierno.
  2. ❌ Ejecutar trading.

---

### 💹 Sub-departamento 3.2: TRADING (Ejecución Financiera)

#### 📋 Script Jefe: `trading/engine.py`
- **Rol:** El Ejecutor Blindado
- **Misión:** Analizar mercados, calcular riesgo y ejecutar órdenes solo con autorización temporal.
- **Deberes:**
  1. Verificar Circuit Breaker (win_rate < 40% = bloqueo).
  2. Consultar `AUTO_EJECUCION_TEMP` en Redis antes de ejecutar.
  3. Integrar Position Sizer con factor 0.4 de seguridad.
  4. Integrar Risk Manager para validación de VIX.
- **Prohibiciones:**
  1. ❌ Enviar mensajes a Telegram (usa `telegram/utils.py`).
  2. ❌ Manejar memoria conversacional (usa `parliament/core.py`).
  3. ❌ Ejecutar sin autorización temporal válida.

#### 📋 Script Jefe: `trading/risk_manager.py`
- **Rol:** El Firewall Matemático (Art. 14)
- **Misión:** Bloquear operaciones si las condiciones de mercado son adversas (VIX > 20).
- **Deberes:**
  1. Consultar volatilidad de SPY como proxy del VIX.
  2. Devolver `False` si el riesgo excede el límite constitucional.
  3. Aplicar principio Fail-Closed (si no puede verificar, bloquea).
- **Prohibiciones:**
  1. ❌ Ejecutar órdenes de trading.
  2. ❌ Enviar mensajes a Telegram.

#### 📋 Script Jefe: `trading/strategy_engine.py`
- **Rol:** El Estratega Cuantitativo
- **Misión:** Evaluar estrategias de trading (RSI + Volumen) sobre datos históricos.
- **Deberes:**
  1. Calcular RSI con ventana móvil de 14 periodos.
  2. Confirmar volumen sobre promedio.
  3. Devolver señales: COMPRA, VENTA o ESPERA.
- **Prohibiciones:**
  1. ❌ Ejecutar órdenes.
  2. ❌ Modificar datos de mercado.

#### 📋 Script Jefe: `trading/position_sizer.py`
- **Rol:** La Calculadora de Riesgo
- **Misión:** Calcular el tamaño exacto de posición para que el riesgo nunca exceda 1% (Art. 14) con factor 0.4 de seguridad.
- **Deberes:**
  1. Aplicar fórmula: `acciones = (capital * 0.01 * 0.4) / riesgo_por_acción`.
  2. Rechazar operaciones si el capital es insuficiente.
- **Prohibiciones:**
  1. ❌ Ejecutar órdenes.
  2. ❌ Modificar estrategias.

---

### 📡 Sub-departamento 3.3: TELECOMUNICACIONES

#### 📋 Script Jefe: `telegram/utils.py`
- **Rol:** El Mensajero Oficial
- **Misión:** Traducir decisiones del sistema a mensajes de Telegram con formato Markdown.
- **Deberes:**
  1. Respetar límite de 250 palabras por mensaje.
  2. Soportar botones inline (reply_markup).
  3. Nunca fallar silenciosamente.
- **Prohibiciones:**
  1. ❌ Tomar decisiones de trading.
  2. ❌ Almacenar datos localmente.

---

### 🤖 Sub-departamento 3.4: AUTONOMÍA

#### 📋 Script Jefe: `autonomy/backtester.py`
- **Rol:** El Historiador de Mercado
- **Misión:** Simular operaciones históricas para validar estrategias antes de operar en vivo.
- **Deberes:**
  1. Usar 100% API nativa de Alpaca (sin yfinance).
  2. Calcular Win Rate, Drawdown y Retorno Total.
  3. Devolver veredicto: APTO o REQUIERE AJUSTE.
- **Prohibiciones:**
  1. ❌ Ejecutar órdenes en tiempo real.
  2. ❌ Modificar estrategias.

---

## 🚨 REGLAS TRANSVERSALES (APLICAN A TODOS LOS SCRIPTS)

1. **Principio Anticaos (Art. 9):** Ningún script puede crear archivos fuera de su departamento.
2. **Principio de Soberanía (Art. 12):** Todas las credenciales deben venir de variables de entorno, nunca hardcodeadas.
3. **Principio de Trazabilidad (Art. 11):** Cada cambio crítico debe tener etiqueta `[MOD-YYYY-MM-DD] [AUTOR] [VALIDADOR]`.
4. **Principio de Protección Patrimonial (Art. 14):** Ningún script puede ejecutar trading sin pasar por `risk_manager.py` y `position_sizer.py`.

---

## 🔍 AUDITORÍA DE CUMPLIMIENTO

El script `SOBERANO_00_GOBIERNO/auditor_de_roles.py` (Fase 1 - Paso 3) verificará:
- ✅ Que cada `.py` tenga su Ficha de Identidad en la cabecera.
- ✅ Que ningún script viole sus Prohibiciones.
- ✅ Que no existan scripts huérfanos sin departamento asignado.

**Frecuencia de auditoría:**
- Pre-deploy: Cada `git push` (GitHub Actions).
- Periódica: Cada 24 horas (cron job).
- Bajo demanda: Comando `/auditar_roles` en Telegram.

---

## 📝 CHANGELOG

| Fecha | Versión | Cambio | Autor |
|-------|---------|--------|-------|
| 2026-07-30 | 1.0 | Creación inicial del manifiesto | Qwen / JEISSON_01 |

---

*Este documento es la Constitución Operativa del sistema. Cualquier modificación debe ser aprobada por el Director JEISSON_01 y registrada en este changelog.*
