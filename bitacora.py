#!/usr/bin/env python3
"""
Sistema de Bitácora Única - Maestro-Nexus
Historial completo, trazabilidad total, consulta obligatoria.
"""
import sys
import hashlib
from datetime import datetime

BITACORA_PATH = "BITACORA.md"

def obtener_ultimo_hash():
    try:
        with open(BITACORA_PATH, "r", encoding="utf-8") as f:
            contenido = f.read()
        hashes = contenido.split("**Hash actual:** ")
        if len(hashes) > 1:
            return hashes[-1].split("\n")[0].strip()
    except FileNotFoundError:
        pass
    return "0" * 64

def calcular_hash(contenido):
    return hashlib.sha256(contenido.encode()).hexdigest()

def consultar(ultimas=5):
    try:
        with open(BITACORA_PATH, "r", encoding="utf-8") as f:
            contenido = f.read()
        entradas = contenido.split("---\n## [")
        print(f"\n📋 ÚLTIMAS {ultimas} ENTRADAS DE LA BITÁCORA\n")
        for entrada in entradas[-ultimas:]:
            if entrada.strip():
                lineas = entrada.split("\n")
                print(f"📌 [{lineas[0]}")
                for linea in lineas[1:8]:
                    if linea.strip():
                        print(f"   {linea}")
                print()
    except FileNotFoundError:
        print("⚠️ Bitácora vacía.")

def marcar_completado(id_entrada):
    try:
        with open(BITACORA_PATH, "r", encoding="utf-8") as f:
            contenido = f.read()
        
        if f"[{id_entrada}]" in contenido:
            # Reemplazar solo la primera ocurrencia de [EN_PROGRESO] en esa entrada específica
            partes = contenido.split(f"[{id_entrada}]")
            if len(partes) > 1:
                resto = partes[1].replace("[EN_PROGRESO]", "[COMPLETADA]", 1)
                contenido = partes[0] + f"[{id_entrada}]" + resto
                
                with open(BITACORA_PATH, "w", encoding="utf-8") as f:
                    f.write(contenido)
                print(f"✅ Entrada {id_entrada} marcada como COMPLETADA")
            else:
                print(f"❌ Formato no encontrado para {id_entrada}")
        else:
            print(f"❌ No se encontró la entrada {id_entrada}")
    except Exception as e:
        print(f"❌ Error: {e}")

def buscar(palabra):
    try:
        with open(BITACORA_PATH, "r", encoding="utf-8") as f:
            contenido = f.read()
        entradas = contenido.split("---\n## [")
        resultados = [e for e in entradas if palabra.lower() in e.lower()]
        print(f"\n🔍 RESULTADOS PARA '{palabra}': {len(resultados)} entradas\n")
        for r in resultados[:5]:
            print(f"📌 [{r.split(chr(10))[0]}")
    except FileNotFoundError:
        print("⚠️ Bitácora vacía.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 bitacora.py [--consulta|--buscar|--completar]")
        print("  --consulta [N]      Muestra últimas N entradas (default: 5)")
        print("  --buscar PALABRA    Busca entradas que contengan PALABRA")
        print("  --completar ID      Marca entrada ID como COMPLETADA")
    elif sys.argv[1] == "--consulta":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        consultar(n)
    elif sys.argv[1] == "--buscar" and len(sys.argv) > 2:
        buscar(sys.argv[2])
    elif sys.argv[1] == "--completar" and len(sys.argv) > 2:
        marcar_completado(sys.argv[2])
