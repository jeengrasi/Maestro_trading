#!/usr/bin/env python3
# ==============================================================================
# ARCHIVO: auditor_de_roles.py
# MODULO: gobierno
# DEPARTAMENTO: 00 - GOBIERNO
# SISTEMA: MAESTRO-NEXUS
# ROL: El Auditor Automático de Cumplimiento
# MISIÓN: Verificar que todos los scripts cumplan con su Ficha de Identidad y no violen sus prohibiciones.
# ==============================================================================
import os
import re
import sys

def main():
    print("🛡️ INICIANDO AUDITORÍA DE ROLES Y CUMPLIMIENTO...")
    print("=" * 80)
    
    errores = []
    scripts_dir = "SOBERANO_03_NEXUS"
    
    if not os.path.exists(scripts_dir):
        print(f"❌ Directorio {scripts_dir} no encontrado.")
        sys.exit(1)
        
    # 1. Recopilar todos los archivos .py
    py_files = []
    for root, dirs, files in os.walk(scripts_dir):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.venv', 'venv']]
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
                
    print(f"📂 Escaneando {len(py_files)} archivos Python...")
    
    # 2. Verificar Ficha de Identidad en cada archivo
    for filepath in py_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar marcadores de identidad
        if "# DEPARTAMENTO:" not in content:
            errores.append(f"❌ {filepath}: NO TIENE FICHA DE IDENTIDAD (Falta '# DEPARTAMENTO:')")
        if "# ROL:" not in content:
            errores.append(f"❌ {filepath}: NO TIENE FICHA DE IDENTIDAD (Falta '# ROL:')")
            
        # 3. Verificar Violaciones de Prohibiciones (Reglas básicas de seguridad)
        filename = os.path.basename(filepath)
        
        # Regla A: Scripts de trading NO deben enviar mensajes a Telegram directamente
        if 'trading' in filepath and 'send_telegram' in content and 'utils.py' not in filepath:
            errores.append(f"🚨 VIOLACIÓN DE ROL en {filepath}: Los scripts de trading no pueden llamar a 'send_telegram' directamente.")
            
        # Regla B: Scripts de Telegram NO deben contener lógica de ejecución de órdenes
        if 'telegram' in filepath and ('execute_order' in content or 'submit_order' in content):
            errores.append(f"🚨 VIOLACIÓN DE ROL en {filepath}: Los scripts de telecomunicaciones no pueden ejecutar órdenes de trading.")
            
        # Regla C: Credenciales hardcodeadas (búsqueda básica)
        if re.search(r'(?:api_key|secret|token)\s*=\s*["\'][a-zA-Z0-9_\-]{10,}["\']', content, re.IGNORECASE):
            if not content.strip().startswith('#'): # Ignorar comentarios
                errores.append(f"🚨 VIOLACIÓN DE SEGURIDAD en {filepath}: Posible credencial hardcodeada detectada.")

    # 4. Reporte Final
    print("=" * 80)
    if not errores:
        print("✅ AUDITORÍA EXITOSA: Todos los scripts cumplen con sus roles y prohibiciones.")
        print("🟢 ESTADO DEL SISTEMA: 100% SOBERANO Y CONSTITUCIONAL.")
        sys.exit(0)
    else:
        print("🔴 AUDITORÍA FALLIDA: Se detectaron violaciones constitucionales:")
        for err in errores:
            print(f"   {err}")
        print("\n⚠️ ACCIÓN REQUERIDA: Corrija las violaciones antes de hacer deploy.")
        sys.exit(1)

if __name__ == "__main__":
    main()
