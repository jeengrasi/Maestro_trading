#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "⚙️ REFACTORIZANDO SOBERANO_02_CORE/core/scheduler.py..."

# Reemplazar scheduler.py con la versión optimizada y limpia
cat > SOBERANO_02_CORE/core/scheduler.py << 'EOF_PY'
#!/usr/bin/env python3
"""
Módulo de Planificación y Coordinación Temporal - Parlamento Nexus
Garantiza ejecuciones cíclicas sin bloqueo de memoria y con manejo estricto de excepciones.
"""

import sys
import os
import time
from datetime import datetime

BITACORA_PATH = "SOBERANO_01_MEMORIA/bitacora.md"

def registrar_evento(mensaje: str, tipo: str = "INFO") -> None:
    """Registra eventos en la bitácora del sistema con formato estándar."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{tipo}] [SCHEDULER] {mensaje}\n"
    try:
        os.makedirs(os.path.dirname(BITACORA_PATH), exist_ok=True)
        with open(BITACORA_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        sys.stderr.write(f"Error al escribir en bitácora: {e}\n")

def verificar_entorno() -> bool:
    """Verifica la existencia de directorios clave del Parlamento."""
    rutas_requeridas = ["SOBERANO_00_GOBIERNO", "SOBERANO_01_MEMORIA", "SOBERANO_02_CORE"]
    for ruta in rutas_requeridas:
        if not os.path.exists(ruta):
            registrar_evento(f"Ruta crítica ausente: {ruta}", "ERROR")
            return False
    return True

def ejecutar_ciclo() -> int:
    """Coordina la rutina del scheduler."""
    registrar_evento("Inicio de verificación de rutina cíclica.")
    if not verificar_entorno():
        registrar_evento("Verificación de entorno fallida.", "FAIL")
        return 1
    
    registrar_evento("Entorno verificado correctamente. Estado: OK.", "PASS")
    return 0

if __name__ == "__main__":
    codigo_salida = ejecutar_ciclo()
    sys.exit(codigo_salida)
EOF_PY

# Mover script de refactor al historial
mv refactor_scheduler.sh SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS/ 2>/dev/null || true

echo "🛡️ Pasando scheduler.py por la tubería de veeduría..."
./SOBERANO_00_GOBIERNO/nexus_cli.sh veeduria SOBERANO_02_CORE/core/scheduler.py --dry-run
