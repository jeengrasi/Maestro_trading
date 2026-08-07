# 🏛️ INFORME DE AUDITORÍA ARQUITECTÓNICA Y PROPUESTA DE MODULARIZACIÓN
**Fecha:** 2026-08-06
**Alcance:** Análisis estático de código para identificar oportunidades de refactorización.

---
## 1. RANKING DE ARCHIVOS POR TAMAÑO (Oportunidades de División)
*(Archivos con >150 líneas son candidatos prioritarios a refactorización)*

- `SOBERANO_03_NEXUS/trading/risk_manager.py`: **286 líneas** ⚠️ **MONOLÍTICO**- `SOBERANO_03_NEXUS/parliament/core.py`: **255 líneas** ⚠️ **MONOLÍTICO**- `SOBERANO_03_NEXUS/trading/strategy_engine.py`: **216 líneas** ⚠️ **MONOLÍTICO**- `SOBERANO_03_NEXUS/telegram/commands.py`: **190 líneas** ⚠️ **MONOLÍTICO**- `SOBERANO_03_NEXUS/core/commands.py`: **179 líneas** ⚠️ **MONOLÍTICO**- `SOBERANO_03_NEXUS/core/router.py`: **177 líneas** ⚠️ **MONOLÍTICO**- `SOBERANO_03_NEXUS/core/diagnostics.py`: **161 líneas** ⚠️ **MONOLÍTICO**- `SOBERANO_03_NEXUS/index.py`: **160 líneas** ⚠️ **MONOLÍTICO**- `SOBERANO_03_NEXUS/autonomy/position_monitor.py`: **154 líneas** ⚠️ **MONOLÍTICO**- `SOBERANO_03_NEXUS/parliament/tool_caller.py`: **147 líneas**- `SOBERANO_03_NEXUS/trading/engine.py`: **146 líneas**- `SOBERANO_03_NEXUS/autonomy/backtester.py`: **134 líneas**- `SOBERANO_03_NEXUS/core/contralor.py`: **130 líneas**- `SOBERANO_03_NEXUS/telegram/formatters.py`: **124 líneas**- `SOBERANO_03_NEXUS/autonomy/scheduler.py`: **119 líneas**- `SOBERANO_03_NEXUS/core/memory_updater.py`: **114 líneas**- `SOBERANO_03_NEXUS/autonomy/reflexion_agent.py`: **113 líneas**- `SOBERANO_02_CORE/core/scheduler.py`: **86 líneas**- `SOBERANO_03_NEXUS/nexus_bridge.py`: **85 líneas**- `SOBERANO_03_NEXUS/telegram/webhook.py`: **75 líneas**- `SOBERANO_03_NEXUS/parliament/github_rag.py`: **74 líneas**- `SOBERANO_03_NEXUS/trading/priority.py`: **72 líneas**- `SOBERANO_03_NEXUS/core/memory_logger.py`: **72 líneas**- `SOBERANO_02_CORE/core/generar_bitacora.py`: **69 líneas**- `SOBERANO_03_NEXUS/telegram/inline_actions.py`: **67 líneas**- `SOBERANO_03_NEXUS/core/memory.py`: **67 líneas**- `SOBERANO_03_NEXUS/core/guardian.py`: **54 líneas**- `SOBERANO_03_NEXUS/config.py`: **49 líneas**- `SOBERANO_03_NEXUS/providers/mistral.py`: **44 líneas**- `SOBERANO_03_NEXUS/providers/groq.py`: **38 líneas**- `SOBERANO_03_NEXUS/providers/openrouter.py`: **38 líneas**- `SOBERANO_03_NEXUS/trading/position_sizer.py`: **37 líneas**- `SOBERANO_03_NEXUS/telegram/utils.py`: **35 líneas**- `SOBERANO_03_NEXUS/setup_webhook.py`: **26 líneas**- `SOBERANO_03_NEXUS/trading/__init__.py`: **24 líneas**- `SOBERANO_03_NEXUS/autonomy/__init__.py`: **24 líneas**- `SOBERANO_03_NEXUS/router.py`: **22 líneas**- `SOBERANO_03_NEXUS/parliament/classifier.py`: **21 líneas**- `SOBERANO_03_NEXUS/parliament/debate.py`: **19 líneas**- `SOBERANO_03_NEXUS/parliament/actas.py`: **18 líneas**- `SOBERANO_03_NEXUS/parliament/manager.py`: **15 líneas**- `SOBERANO_03_NEXUS/__init__.py`: **13 líneas**- `SOBERANO_03_NEXUS/providers/__init__.py`: **13 líneas**- `SOBERANO_03_NEXUS/parliament/__init__.py`: **13 líneas**- `SOBERANO_03_NEXUS/telegram/__init__.py`: **13 líneas**- `SOBERANO_03_NEXUS/core/__init__.py`: **13 líneas**
---
## 2. MAPA DE DEPENDENCIAS CRÍTICAS
*(Muestra qué archivos dependen de módulos internos del sistema)*

- **`SOBERANO_02_CORE/core/scheduler.py`** depende de:  - `SOBERANO_03_NEXUS.config.Config`  - `SOBERANO_03_NEXUS.trading.engine.TradingEngine`- **`SOBERANO_03_NEXUS/router.py`** depende de:  - `SOBERANO_03_NEXUS.parliament.core.call_ia`  - `SOBERANO_03_NEXUS.parliament.core.PARLIAMENT_STACK`  - `SOBERANO_03_NEXUS.parliament.actas.generate_acta`  - `SOBERANO_03_NEXUS.parliament.actas.save_acta_to_github`  - `SOBERANO_03_NEXUS.parliament.debate.handle_parliament_debate`  - *(y 3 más...)*- **`SOBERANO_03_NEXUS/index.py`** depende de:  - `SOBERANO_03_NEXUS.telegram.webhook.router`  - `SOBERANO_03_NEXUS.core.guardian.verify_startup_requirements`- **`SOBERANO_03_NEXUS/parliament/core.py`** depende de:  - `SOBERANO_03_NEXUS.parliament.tool_caller.MISTRAL_TOOLS`  - `SOBERANO_03_NEXUS.providers.mistral.call_mistral`  - `SOBERANO_03_NEXUS.parliament.github_rag.obtener_contexto_gobierno`  - `SOBERANO_03_NEXUS.parliament.tool_caller.execute_tool`- **`SOBERANO_03_NEXUS/telegram/commands.py`** depende de:  - `SOBERANO_03_NEXUS.config.Config`  - `SOBERANO_03_NEXUS.telegram.formatters.format_posiciones_abiertas`  - `alpaca.trading.client.TradingClient`  - `SOBERANO_03_NEXUS.telegram.formatters.format_estado`  - `SOBERANO_03_NEXUS.telegram.formatters.format_historial`- **`SOBERANO_03_NEXUS/telegram/webhook.py`** depende de:  - `SOBERANO_03_NEXUS.telegram.commands.CommandProcessor`  - `SOBERANO_03_NEXUS.config.Config`  - `SOBERANO_03_NEXUS.telegram.utils.send_telegram`- **`SOBERANO_03_NEXUS/trading/engine.py`** depende de:  - `SOBERANO_03_NEXUS.config.Config`  - `SOBERANO_03_NEXUS.telegram.utils.send_telegram`  - `alpaca.trading.requests.MarketOrderRequest`  - `SOBERANO_03_NEXUS.telegram.formatters.format_nueva_posicion`  - `alpaca.trading.enums.OrderClass`  - *(y 6 más...)*- **`SOBERANO_03_NEXUS/autonomy/scheduler.py`** depende de:  - `SOBERANO_03_NEXUS.trading.engine.analizar_y_ejecutar_sombra`  - `SOBERANO_03_NEXUS.trading.priority.obtener_activo_prioritario`  - `SOBERANO_03_NEXUS.trading.priority.calcular_score_prioridad`  - `SOBERANO_03_NEXUS.trading.priority.actualizar_prioridad_en_redis`- **`SOBERANO_03_NEXUS/autonomy/backtester.py`** depende de:  - `SOBERANO_03_NEXUS.trading.position_sizer.calcular_tamano_posicion`- **`SOBERANO_03_NEXUS/autonomy/position_monitor.py`** depende de:  - `SOBERANO_03_NEXUS.telegram.formatters.format_cierre_posicion`  - `SOBERANO_03_NEXUS.config.Config`  - `SOBERANO_03_NEXUS.telegram.utils.send_telegram`  - `SOBERANO_03_NEXUS.telegram.formatters.format_resumen_diario`  - `alpaca.trading.client.TradingClient`- **`SOBERANO_03_NEXUS/core/router.py`** depende de:  - `SOBERANO_03_NEXUS.config.Config`  - `SOBERANO_03_NEXUS.telegram.utils.send_telegram`  - `SOBERANO_03_NEXUS.core.memory_logger.registrar_en_bitacora`  - `SOBERANO_03_NEXUS.parliament.core.call_ia`  - `SOBERANO_03_NEXUS.trading.engine.analizar_y_ejecutar_sombra`  - *(y 2 más...)*- **`SOBERANO_03_NEXUS/core/diagnostics.py`** depende de:  - `SOBERANO_03_NEXUS.config.Config`- **`SOBERANO_03_NEXUS/core/commands.py`** depende de:  - `SOBERANO_03_NEXUS.config.Config`  - `SOBERANO_03_NEXUS.trading.engine.get_alpaca_client`  - `SOBERANO_03_NEXUS.autonomy.reflexion_agent.generar_reflexion_y_propuesta`  - `SOBERANO_02_CORE.core.generar_bitacora.generar_bitacora`  - `SOBERANO_02_CORE.core.scheduler.get_scheduler`
---
## 3. HALLAZGOS Y RECOMENDACIONES DE MODULARIZACIÓN
### 🔍 Hallazgo 1: El Rol de `index.py`
- **Problema:** `SOBERANO_03_NEXUS/index.py` tiene 160 líneas. Mezcla configuración, enrutamiento y posiblemente lógica.
- **Propuesta:** Convertirlo en una 'Application Factory' pura (< 40 líneas) que solo inicialice FastAPI, invoque al Guardián y registre los `routers` ya modularizados.

### 🔍 Hallazgo 2: Duplicidad de Nombres (Scheduler y Router)
- **Problema:** Existen múltiples `scheduler.py`: SOBERANO_03_NEXUS/autonomy/scheduler.py, SOBERANO_02_CORE/core/scheduler.py. Esto genera ambigüedad sobre cuál es el activo.
- **Propuesta:** Auditar cuál es importado realmente por `index.py` o el motor principal. Eliminar o fusionar el obsoleto.
- **Problema:** Existen múltiples `router.py`: SOBERANO_03_NEXUS/core/router.py, SOBERANO_03_NEXUS/providers/openrouter.py, SOBERANO_03_NEXUS/router.py.
- **Propuesta:** Unificar en un solo `api/router.py` o `core/router.py` que agrupe todos los endpoints, o mantenerlos estrictamente separados por dominio (ej: `telegram/router.py` vs `api/router.py`).

### 🔍 Hallazgo 3: Integración Telegram <-> Trading
- **Advertencia:** Los módulos de Telegram importan lógica de trading directamente. Esto viola el principio de separación de responsabilidades.

---
## 4. ARQUITECTURA OBJETIVO PROPUESTA
```text
SOBERANO_03_NEXUS/
├── index.py                 # < 40 líneas. Solo: Guardián + FastAPI() + include_router()
├── config.py                # Carga y validación de variables de entorno (.env)
├── core/
│   ├── guardian.py          # Validación Hard-Fail de arranque
│   └── router.py            # (Opcional) Enrutador principal de la API
├── telegram/
│   ├── webhook.py           # Recibe updates de Telegram
│   ├── commands.py          # Lógica de /estado, /autorizar, etc.
│   └── router.py            # Agrupa los endpoints de Telegram
└── trading/
    ├── engine.py            # Orquestador de la estrategia
    ├── risk_manager.py      # Firewall matemático (Drawdown, tamaño de posición)
    └── strategy_engine.py   # Cálculo de indicadores (EMA, RSI, etc.)
```
