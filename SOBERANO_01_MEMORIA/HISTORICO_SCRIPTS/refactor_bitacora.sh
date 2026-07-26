#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "⚙️ REFACTORIZANDO SOBERANO_02_CORE/core/generar_bitacora.py..."

cat > SOBERANO_02_CORE/core/generar_bitacora.py << 'EOF_PY'
#!/usr/bin/env python3
"""
Módulo Generador de Bitácora y Auditoría Continua - Parlamento Nexus
Gestiona la escritura, validación y control de volumen del archivo de bitácora.
"""

import sys
import os
from datetime import datetime

BITACORA_PATH = "SOBERANO_01_MEMORIA/bitacora.md"
MAX_LINEAS = 450

def asegurar_estructura() -> None:
    """Crea el directorio de memoria y la bitácora si no existen."""
    os.makedirs(os.path.dirname(BITACORA_PATH), exist_ok=True)
    if not os.path.exists(BITACORA_PATH):
        with open(BITACORA_PATH, "w", encoding="utf-8") as f:
            f.write("# 📜 BITÁCORA DEL SISTEMA PARLAMENTO NEXUS\n")
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [SYSTEM] Bitácora inicializada.\n")

def obtener_conteo_lineas() -> int:
    """Devuelve el número actual de líneas en la bitácora."""
    asegurar_estructura()
    try:
        with open(BITACORA_PATH, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception as e:
        sys.stderr.write(f"Error al leer bitácora: {e}\n")
        return 0

def registrar_entrada(modulo: str, mensaje: str, estado: str = "INFO") -> bool:
    """Añade un registro estructurado a la bitácora."""
    asegurar_estructura()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] [{estado}] [{modulo.upper()}] {mensaje}\n"
    
    try:
        with open(BITACORA_PATH, "a", encoding="utf-8") as f:
            f.write(linea)
        return True
    except Exception as e:
        sys.stderr.write(f"Error al registrar entrada: {e}\n")
        return False

def ejecutar_verificacion() -> int:
    """Verifica el estado y volumen de la bitácora."""
    lineas = obtener_conteo_lineas()
    if lineas > MAX_LINEAS:
        registrar_entrada("BITACORA", f"Alerta de volumen: {lineas}/{MAX_LINEAS} líneas.", "WARN")
    else:
        registrar_entrada("BITACORA", f"Verificación de rutina completada ({lineas}/{MAX_LINEAS} líneas).", "PASS")
    return 0

if __name__ == "__main__":
    sys.exit(ejecutar_verificacion())
EOF_PY

mv refactor_bitacora.sh SOBERANO_01_MEMORIA/HISTORICO_SCRIPTS/ 2>/dev/null || true

echo "🛡️ Pasando generar_bitacora.py por la tubería de veeduría..."
./SOBERANO_00_GOBIERNO/nexus_cli.sh veeduria SOBERANO_02_CORE/core/generar_bitacora.py --dry-run
