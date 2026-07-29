#!/usr/bin/env python3
"""
Módulo de Rastreo EAD de Rutas e Imports - Parlamento Nexus
Escanea el proyecto para identificar referencias legacy a 'api.' o rutas no resueltas.
"""

import os
import sys
import re
from datetime import datetime

BITACORA_PATH = "SOBERANO_01_MEMORIA/bitacora.md"

def registrar_evento(mensaje: str, tipo: str = "INFO") -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{tipo}] [RASTREO_EAD] {mensaje}\n"
    try:
        os.makedirs(os.path.dirname(BITACORA_PATH), exist_ok=True)
        with open(BITACORA_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        sys.stderr.write(f"Error escribiendo en bitácora: {e}\n")

def escanear_imports_legacy():
    print("======================================================")
    print("   🔍 AUDITORÍA DE RUTAS E IMPORTS (EAD SANITY CHECK) ")
    print("======================================================")
    
    patron_import = re.compile(r"^\s*(from|import)\s+(api[\.\s\w]*|SOBERANO_[\.\s\w]*)", re.MULTILINE)
    
    hallazgos = []
    
    for root, _, files in os.walk("."):
        if "HISTORICO_SCRIPTS" in root or ".git" in root or "__pycache__" in root:
            continue
            
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        lineas = f.readlines()
                        for num, linea in enumerate(lineas, 1):
                            if "from api" in linea or "import api" in linea or "from SOBERANO_" in linea:
                                hallazgos.append((filepath, num, linea.strip()))
                except Exception as e:
                    registrar_evento(f"Error leyendo {filepath}: {e}", "WARN")

    if hallazgos:
        print(f"\n📍 Se encontraron {len(hallazgos)} referencia(s) de importación:\n")
        for file, line, text in hallazgos:
            print(f"  • {file}:{line} --> {text}")
        registrar_evento(f"Rastreos encontrados: {len(hallazgos)} líneas de importación.", "PASS")
    else:
        print("\n✅ No se encontraron importaciones activas conflicto en los módulos escaneados.")
        registrar_evento("Escaneo completado sin conflictos detectados.", "PASS")

    return 0

if __name__ == "__main__":
    sys.exit(escanear_imports_legacy())
