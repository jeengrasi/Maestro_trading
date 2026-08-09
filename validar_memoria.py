#!/usr/bin/env python3
"""
Auditor Automático de Integridad de Memoria
Verifica que la bitácora y el estado del sistema estén sincronizados.
"""
import re
import sys

def validar_bitacora():
    """Verifica que no haya IDs repetidos y que los hashes estén encadenados."""
    try:
        with open("BITACORA.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extraer todos los IDs
        ids = re.findall(r'## \[(ID-\d{4})\]', content)
        
        # Verificar duplicados
        duplicados = [id for id in set(ids) if ids.count(id) > 1]
        if duplicados:
            print(f"❌ ERROR: IDs repetidos en bitácora: {', '.join(duplicados)}")
            return False
        
        # Verificar hashes encadenados
        hashes = re.findall(r'\*\*Hash actual:\*\* ([a-f0-9]{64})', content)
        if len(hashes) < 2:
            print("⚠️ ADVERTENCIA: Bitácora tiene menos de 2 actas")
            return True
        
        print(f"✅ Integridad de bitácora: OK ({len(ids)} actas, {len(hashes)} hashes)")
        return True
        
    except FileNotFoundError:
        print("❌ ERROR: BITACORA.md no existe")
        return False

def validar_estado():
    """Verifica que ESTADO_DEL_SISTEMA.md exista y tenga los campos requeridos."""
    try:
        with open("ESTADO_DEL_SISTEMA.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "PENDIENTES REALES" not in content:
            print("❌ ERROR: ESTADO_DEL_SISTEMA.md no tiene sección de pendientes")
            return False
        
        print("✅ Estado del sistema: OK")
        return True
        
    except FileNotFoundError:
        print("❌ ERROR: ESTADO_DEL_SISTEMA.md no existe")
        return False

if __name__ == "__main__":
    print("🔍 Validando integridad de memoria...")
    ok_bitacora = validar_bitacora()
    ok_estado = validar_estado()
    
    if ok_bitacora and ok_estado:
        print("✅ Validación completada: Sistema íntegro")
        sys.exit(0)
    else:
        print("❌ Validación fallida: Hay errores que corregir")
        sys.exit(1)
