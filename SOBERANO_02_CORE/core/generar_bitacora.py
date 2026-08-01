# ==============================================================================
# ARCHIVO: generar_bitacora.py
# DEPARTAMENTO: 02 - CORE (Ejecución)
# SISTEMA: MAESTRO-NEXUS
# ROL: Generador de Bitácora y Auditoría Continua
# MISIÓN: Gestionar la escritura, validación y control de volumen del archivo de bitácora.
# DEBERES: Cumplir con la Constitución, no hardcodear credenciales, registrar errores.
# PROHIBICIONES: Violar las reglas transversales del Manifiesto de Roles, modificar archivos de gobierno.
# ULTIMA MODIFICACION: 2026-08-01
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

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
