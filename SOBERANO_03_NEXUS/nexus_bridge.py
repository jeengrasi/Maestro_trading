#!/usr/bin/env python3
# ==============================================================================
# ARCHIVO: nexus_bridge.py
# DEPARTAMENTO: 03 - NEXUS (Raíz)
# SISTEMA: MAESTRO-NEXUS
# ROL: Puente de Comunicación
# MISIÓN: Facilitar la comunicación entre módulos desacoplados del sistema.
# DEBERES: Cumplir con la Constitución, no hardcodear credenciales, registrar errores.
# PROHIBICIONES: Violar las reglas transversales del Manifiesto de Roles.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

"""
Módulo Bridge de Exploración y Conexión Dinámica - Parlamento Nexus
Detecta dinámicamente qué APIs y servicios están disponibles en el entorno local (Art. 12).
"""

import sys
import os
import re
from datetime import datetime

BITACORA_PATH = "SOBERANO_01_MEMORIA/bitacora.md"
ENV_PATH = ".env"

def registrar_evento(mensaje: str, tipo: str = "INFO") -> None:
    """Registra eventos en la bitácora del sistema."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{tipo}] [NEXUS_BRIDGE] {mensaje}\n"
    try:
        os.makedirs(os.path.dirname(BITACORA_PATH), exist_ok=True)
        with open(BITACORA_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        sys.stderr.write(f"Error escribiendo en bitácora: {e}\n")

def escanear_apis_disponibles() -> list:
    """
    Escanea las variables de entorno y el archivo .env para encontrar
    qué APIs están configuradas, sin asumir proveedores fijos.
    """
    apis_detectadas = set()
    patron_llaves = re.compile(r"^[A-Z0-9_]*(KEY|TOKEN|SECRET|API)[A-Z0-9_]*$")

    # 1. Escanear variables del sistema
    for var in os.environ.keys():
        if patron_llaves.match(var):
            apis_detectadas.add(var)

    # 2. Escanear archivo .env local si existe (sin exponer valores)
    if os.path.exists(ENV_PATH):
        try:
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                for linea in f:
                    linea = linea.strip()
                    if linea and not linea.startswith("#") and "=" in linea:
                        nombre_var = linea.split("=")[0].strip()
                        if patron_llaves.match(nombre_var):
                            apis_detectadas.add(nombre_var)
        except Exception as e:
            registrar_evento(f"Error al leer .env: {e}", "WARN")

    return sorted(list(apis_detectadas))

def diagnostico_puente() -> int:
    """Ejecuta la validación de APIs disponibles en el entorno."""
    registrar_evento("Iniciando escaneo dinámico de conectores y APIs...")
    
    apis = escanear_apis_disponibles()
    
    if apis:
        registrar_evento(f"APIs/Servicios detectados ({len(apis)}): {', '.join(apis)}", "PASS")
        print(f"✅ Escaneo completado. Se detectaron {len(apis)} proveedor(es) configurado(s):")
        for api in apis:
            print(f"  • {api}: DISPONIBLE")
    else:
        registrar_evento("No se detectaron variables de API en el entorno local.", "WARN")
        print("⚠️ No se detectaron variables de API configuradas en el entorno actual.")

    return 0

if __name__ == "__main__":
    sys.exit(diagnostico_puente())
