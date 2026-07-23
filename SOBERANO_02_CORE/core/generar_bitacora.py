#!/usr/bin/env python3
# ================================================
# MAESTRO-NEXUS | GENERADOR DE BITÁCORA V2
# ================================================
# ID: api/core/generar_bitacora.py
# COMMIT: generar_bitacora_v2
# FECHA: 2026-07-05
# AUTOR: Gerente (DeepSeek)
# ESTADO: ✅ COMPLETO
# ================================================
# CAMBIOS vs V1:
# - Backup automático (bitacora_backup.md)
# - Registro en logs
# - Retorno de estado para el Scheduler
# ================================================

import os
import shutil
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================================
# CONFIGURACIÓN DE RUTAS
# ================================================

BASE_DIR = os.path.expanduser("~/Maestro_trading")
PLANTILLA_PATH = os.path.join(BASE_DIR, "05-DOCUMENTACION/DOCS/plantilla_bitacora.md")
DESTINO_PATH = os.path.join(BASE_DIR, "04-REGISTROS/DOCS/bitacora.md")
BACKUP_PATH = os.path.join(BASE_DIR, "04-REGISTROS/DOCS/bitacora_backup.md")
LOG_PATH = os.path.join(BASE_DIR, "04-REGISTROS/LOGS/scheduler.log")

# ================================================
# FUNCIÓN PRINCIPAL
# ================================================

def cargar_datos():
    """Carga los datos para llenar la plantilla."""
    return {
        "VERSION": "2.1",
        "FECHA_FUNDACION": "2026-06-23",
        "DIRECTOR": "JEISSON_01",
        "PROPOSITO": "Lograr la libertad financiera del Director mediante un sistema autónomo de trading, inversión y gestión documental impulsado por un parlamento de IAs.",
        "MISION": "Construir un ecosistema de inteligencia artificial autónomo que gestione, invierta y documente decisiones financieras con la precisión de un comité de expertos, operando 24/7 sin intervención humana.",
        "VISION": "Ser el primer 'Director Financiero Digital' del mundo, capaz de superar a los fondos de inversión tradicionales mediante la sinergia de múltiples IAs, memoria perpetua y automejora continua.",
        "VALORES": "1. **Soberanía del Director:** El humano tiene veto absoluto.\n2. **Transparencia Radical:** Toda decisión queda documentada en actas trazables.\n3. **Resiliencia:** El sistema debe proteger el capital por encima de la especulación.\n4. **Agilidad:** La burocracia es enemiga del progreso; se delega en scripts.",
        "ARQUITECTURA": "### Capas del Sistema\n\n| Capa | Componente | Tecnología | Propósito |\n|------|------------|------------|-----------|\n| **Interfaz** | Telegram Bot | Python / Telegram API | Comunicación con el usuario |\n| **Núcleo** | FastAPI Server | Python / Uvicorn | Gestión de webhooks y lógica interna |\n| **Cerebro** | Parlamento de IAs | Mistral, Llama, Groq, OpenRouter | Debate y toma de decisiones |\n| **Memoria Rápida** | Redis Cache | Upstash Redis | Contexto de sesión (24h) |\n| **Memoria Institucional** | GitHub Repo | Markdown / JSON | Actas, documentos y versionado |\n| **Broker** | Alpaca API | Python SDK | Ejecución de operaciones en papel |\n| **Scheduler** | Motor Interno | asyncio / Python | Tareas autónomas programadas |",
        "ESTRUCTURA": "```\nMaestro_trading/\n├── 00-GOBIERNO/\n│   └── DOCS/\n│       ├── NEXUS_MANIFEST.json\n│       ├── constitucion.md\n│       ├── roles.md\n│       └── seguridad/\n├── 01-MEMORIA/\n│   ├── API/\n│   ├── DOCS/\n│   │   └── actas/\n│   └── SCRIPTS/\n├── 02-SISTEMA/\n│   ├── API/\n│   │   └── api/\n│   │       ├── core/\n│   │       ├── parliament/\n│   │       ├── memory/\n│   │       ├── providers/\n│   │       └── telegram/\n│   ├── DOCS/\n│   └── LAYERS/\n├── 03-OPERACIONES/\n│   └── ENGINE/\n│       └── main.py\n├── 04-REGISTROS/\n│   └── DOCS/\n│       ├── bitacora.md\n│       └── bloque_actas.txt\n├── 05-DOCUMENTACION/\n│   └── DOCS/\n│       ├── 00_INDICE.md\n│       └── README.md\n└── 06-MONITOR/\n    └── DOCS/\n```",
        "HERRAMIENTAS": "### Servicios Activos\n\n| Herramienta | Uso | Estado |\n|-------------|-----|--------|\n| **GitHub** | Repositorio y almacenamiento de actas | ✅ Activo |\n| **Vercel** | Hosting de la API (FastAPI) | ✅ Activo |\n| **Railway** | Backend alternativo (webhook) | ⚠️ Con errores |\n| **Upstash Redis** | Memoria rápida (contexto, caché) | ✅ Activo |\n| **Alpaca** | Broker de trading (paper) | ✅ Activo |\n| **Telegram** | Interfaz de usuario | ✅ Activo |\n| **Termux** | Entorno de desarrollo y control | ✅ Activo |",
        "COMANDOS": "| Comando | Función | Estado |\n|---------|---------|--------|\n| `/start` | Mostrar estado del bot | ✅ |\n| `/docs` | Listar documentos indexados | ✅ |\n| `/doc <nombre>` | Consultar documento | ✅ |\n| `/actas` | Listar actas | ✅ |\n| `/balance` | Ver saldo Alpaca | ✅ |\n| `/chatid` | Ver ID del chat | ✅ |\n| `/stop` | Pausar el sistema | ✅ |\n| `/scheduler` | Estado del scheduler | ✅ |\n| `/health` | Estado de servicios | ✅ |\n| `/actualizar_bitacora` | Actualizar Bitácora manualmente | ✅ |",
        "PLAN_EVOLUCION": "| # | Prioridad | Descripción | Plazo |\n|---|-----------|-------------|-------|\n| 1 | **Scheduler Interno** | Tareas autónomas | ✅ IMPLEMENTADO |\n| 2 | **Bitácora Autónoma** | Generación automática | ✅ IMPLEMENTADO |\n| 3 | **Memoria Vectorial** | Búsqueda semántica | 2 semanas |\n| 4 | **Auto‑reparación** | Health checks | 1 semana |\n| 5 | **Rate Limiting** | Control de abusos | 1 semana |",
        "NORMAS": "- **Art. 1 (Soberanía):** El Director es la autoridad única.\n- **Art. 6 (La Mesa):** Cuerpo consultivo compuesto por DeepSeek, Copilot y Gemini.\n- **Art. 10 (Soberanía Documental):** Solo lo indexado en el sistema tiene validez.\n- **Art. 13 (Reforma):** Cambios requieren propuesta formal y debate de Mesa.",
        "BITACORA_CAMBIOS": "| Fecha | Versión | Cambio | Responsable |\n|-------|---------|--------|-------------|\n| 2026-06-23 | v1.0 | Fundación del Parlamento Nexus | JEISSON_01 |\n| 2026-06-30 | v1.7 | Memoria en 3 niveles | Gerente |\n| 2026-07-04 | v2.0 | Comandos /docs, /doc, /actas | Gerente |\n| 2026-07-04 | v2.1 | Scheduler interno | Gerente + CTO |\n| 2026-07-05 | v2.2 | Bitácora autónoma (Fase 2) | Gerente + Mesa |",
        "REFERENCIAS": "- **Repositorio:** https://github.com/jeengrasi/Maestro_trading\n- **Vercel (API):** https://maestro-trading.vercel.app\n- **Actas en GitHub:** https://github.com/jeengrasi/Maestro_trading/tree/main/01-MEMORIA/DOCS/actas\n- **Constitución:** https://github.com/jeengrasi/Maestro_trading/blob/main/00-GOBIERNO/DOCS/constitucion.md",
        "FECHA_ACTUALIZACION": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ELABORADO_POR": "Gerente (DeepSeek)",
        "VALIDADO_POR": "Mesa Parlamentaria (Gemini, Copilot)",
        "APROBADO_POR": "Director JEISSON_01"
    }

def generar_bitacora():
    """
    Genera la Bitácora con backup, logs y manejo de errores.
    
    Returns:
        tuple: (exito: bool, mensaje: str)
    """
    try:
        # ================================================
        # 1. CREAR CARPETA DE LOGS SI NO EXISTE
        # ================================================
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        
        # ================================================
        # 2. BACKUP DE LA BITÁCORA ACTUAL
        # ================================================
        if os.path.exists(DESTINO_PATH):
            shutil.copy(DESTINO_PATH, BACKUP_PATH)
            logger.info(f"✅ Backup creado: {BACKUP_PATH}")
        
        # ================================================
        # 3. LEER PLANTILLA
        # ================================================
        if not os.path.exists(PLANTILLA_PATH):
            logger.error(f"❌ Plantilla no encontrada: {PLANTILLA_PATH}")
            return False, "Plantilla no encontrada"
        
        with open(PLANTILLA_PATH, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # ================================================
        # 4. REEMPLAZAR VARIABLES
        # ================================================
        datos = cargar_datos()
        for key, value in datos.items():
            placeholder = "{{" + key + "}}"
            contenido = contenido.replace(placeholder, value)
        
        # ================================================
        # 5. GUARDAR BITÁCORA
        # ================================================
        with open(DESTINO_PATH, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        logger.info(f"✅ Bitácora actualizada: {DESTINO_PATH}")
        
        # ================================================
        # 6. REGISTRO EN LOG
        # ================================================
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] ✅ Bitácora actualizada correctamente\n")
        
        return True, "Bitácora actualizada exitosamente"
    
    except Exception as e:
        error_msg = f"Error generando Bitácora: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # Registrar error en log
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] ❌ {error_msg}\n")
        
        return False, error_msg

def actualizar_bitacora():
    """Función wrapper para llamar desde el Scheduler."""
    return generar_bitacora()

if __name__ == "__main__":
    exito, msg = generar_bitacora()
    print(f"{'✅' if exito else '❌'} {msg}")
