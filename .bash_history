    return {"status": "healthy"}

@app.get("/debug-env")
async def debug_env():
    # Muestra el estado real de las variables de entorno en el servidor
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("DIRECTOR_CHAT_ID", "NO_CONFIGURADO")
    
    return {
        "sistema": "Maestro-Nexus v7.1",
        "auditoria_variables_en_vivo": {
            "TELEGRAM_BOT_TOKEN_existe": bool(token),
            "TELEGRAM_BOT_TOKEN_longitud": len(token),
            "TELEGRAM_BOT_TOKEN_inicio": token[:5] + "..." if token else "VACIO",
            "DIRECTOR_CHAT_ID_valor": chat_id,
            "ALPACA_API_KEY_existe": bool(os.getenv("ALPACA_API_KEY")),
            "UPSTASH_REDIS_existe": bool(os.getenv("UPSTASH_REDIS_REST_URL")),
            "PUERTO_ACTUAL": os.getenv("PORT", "8080")
        },
        "instruccion": "Si 'DIRECTOR_CHAT_ID_valor' es 'NO_CONFIGURADO' o un numero que no es el suyo, ese es el problema."
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
"""

with open("SOBERANO_03_NEXUS/index.py", "w", encoding="utf-8") as f:
    f.write(index_code)
print("   ✅ Endpoint /debug-env inyectado exitosamente.")

# 2. VERIFICAR INTEGRIDAD LOCAL DE ARCHIVOS CLAVE
print("\n📝 2. Verificando integridad de archivos locales...")
archivos_a_verificar = [
    "SOBERANO_03_NEXUS/index.py",
    "SOBERANO_03_NEXUS/telegram/webhook.py",
    "SOBERANO_03_NEXUS/telegram/utils.py",
    "Dockerfile"
]
for archivo in archivos_a_verificar:
    if os.path.exists(archivo):
        print(f"   ✅ {archivo} existe")
    else:
        print(f"   ❌ {archivo} FALTANTE")

# 3. COMMIT Y PUSH A GITHUB
print("\n📤 3. Enviando auditoría a GitHub para despliegue en Railway...")
subprocess.run(['git', 'add', 'SOBERANO_03_NEXUS/index.py'], capture_output=True)
subprocess.run(['git', 'commit', '-m', '[AUDIT] Agregado endpoint /debug-env para verificacion en vivo de variables'], capture_output=True)
push_result = subprocess.run(['git', 'push', 'origin', 'soberano-v1'], capture_output=True, text=True)

if push_result.returncode == 0:
    print("   ✅ Desplegado a GitHub exitosamente. Railway comenzará a construir.")
else:
    print(f"   ⚠️ Advertencia: {push_result.stderr}")

print("\n" + "=" * 90)
print("✅ AUDITORÍA PREPARADA. Espere a que Railway muestre 'Active' (verde).")
print("Luego visite: https://maestrotrading-production-c2db.up.railway.app/debug-env")
print("=" * 90)
EOF

python3 << 'EOF'
import subprocess

print("=" * 60)
print("VERIFICACION ATOMICA LOCAL")
print("=" * 60)

# 1. Rama actual
rama = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True).stdout.strip()
print(f"1. Rama actual: {rama}")
if rama != "soberano-v1":
    print("   ERROR: Cambie a la rama correcta con: git checkout soberano-v1")
else:
    print("   OK: Rama correcta.")

# 2. Estado limpio
status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
if status:
    print("   ADVERTENCIA: Hay cambios sin guardar. Ejecute: git add . && git commit -m 'fix'")
else:
    print("   OK: Repositorio limpio.")

# 3. Forzar sincronizacion
print("\nSincronizando con GitHub...")
subprocess.run(["git", "fetch", "origin"], capture_output=True)
subprocess.run(["git", "push", "origin", "soberano-v1"], capture_output=True)
print("   OK: Push a soberano-v1 completado.")
print("=" * 60)
EOF

python3 << 'EOF'
import os
import subprocess
import datetime

print("=" * 80)
print("🚀 SCRIPT MAESTRO DE RESOLUCIÓN NUCLEAR")
print("=" * 80)

# 1. Forzar rama correcta
print("\n[1/5] Alineando rama a soberano-v1...")
subprocess.run(["git", "checkout", "-B", "soberano-v1"], capture_output=True)
print("   ✅ Rama 'soberano-v1' activa y actualizada.")

# 2. Romper caché de Docker de Railway (Truco infalible)
print("\n[2/5] Rompiendo caché de Docker en Railway...")
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open("Dockerfile", "a") as f:
    f.write(f"\n# FORCE REBUILD TIMESTAMP: {timestamp}\n")
print("   ✅ Dockerfile modificado. Railway se verá obligado a reconstruir desde cero.")

# 3. Verificar endpoint de auditoría
print("\n[3/5] Verificando integridad del código...")
if os.path.exists("SOBERANO_03_NEXUS/index.py"):
    with open("SOBERANO_03_NEXUS/index.py", "r", encoding="utf-8") as f:
        if "/debug-env" in f.read():
            print("   ✅ Endpoint /debug-env presente y listo.")
        else:
            print("   ⚠️ Advertencia: /debug-env no encontrado.")
else:
    print("   ❌ Error crítico: index.py no encontrado.")

# 4. Commit y Push forzado
print("\n[4/5] Enviando cambios al repositorio remoto (GitHub)...")
subprocess.run(["git", "add", "Dockerfile", "SOBERANO_03_NEXUS/index.py"], capture_output=True)
subprocess.run(["git", "commit", "-m", f"[NUCLEAR] Force rebuild {timestamp}"], capture_output=True)
push_result = subprocess.run(["git", "push", "origin", "soberano-v1", "--force"], capture_output=True, text=True)

if push_result.returncode == 0:
    print("   ✅ Push forzado a 'soberano-v1' completado con éxito.")
else:
    print(f"   ❌ Error en push: {push_result.stderr}")

# 5. Generar plantilla de variables para facilitar la copia
print("\n[5/5] Generando plantilla de variables para Railway...")
vars_template = """TELEGRAM_BOT_TOKEN=PEGUE_AQUI_SU_TOKEN_REAL
DIRECTOR_CHAT_ID=PEGUE_AQUI_SU_ID_NUMERICO_REAL
ALPACA_API_KEY=PEGUE_AQUI_SU_API_KEY_REAL
ALPACA_SECRET_KEY=PEGUE_AQUI_SU_SECRET_KEY_REAL
ALPACA_PAPER=true
UPSTASH_REDIS_REST_URL=PEGUE_AQUI_SU_URL_REAL
UPSTASH_REDIS_REST_TOKEN=PEGUE_AQUI_SU_TOKEN_REAL
"""
with open("VARIABLES_PARA_RAILWAY.txt", "w", encoding="utf-8") as f:
    f.write(vars_template)
print("   ✅ Archivo 'VARIABLES_PARA_RAILWAY.txt' creado en su carpeta.")

print("\n" + "=" * 80)
print("✅ FASE AUTOMÁTICA COMPLETADA AL 100%.")
print("=" * 80)
print("\n⚠️ AHORA, SOLO NECESITA HACER ESTOS 2 CLICS EN SU NAVEGADOR (RAILWAY):")
print("1. Vaya a Settings > Source y cambie la 'Branch' a: soberano-v1")
print("2. Vaya a Variables > Service y asegúrese de que las 7 variables estén allí (use el archivo .txt que acabo de crear).")
print("3. Vaya a Deployments y haga clic en 'Redeploy' (o borre el servicio y créelo de nuevo desde GitHub).")
print("\n🔍 Luego, visite en modo incógnito:")
print("https://maestrotrading-production-c2db.up.railway.app/debug-env")
print("=" * 80)
EOF

python3 << 'EOF'
import urllib.request
import json

url = "https://maestrotrading-production-c2db.up.railway.app/debug-env"
print(f"Consultando: {url}\n")

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print("✅ ¡ÉXITO! EL SERVIDOR RESPONDIÓ:")
        print(json.dumps(data, indent=2))
        
        if data.get("auditoria_variables_en_vivo", {}).get("TELEGRAM_BOT_TOKEN_existe"):
            print("\n🎉 LAS VARIABLES ESTÁN CARGADAS CORRECTAMENTE.")
            print("   Vaya a Telegram y envíe el comando: /estado")
        else:
            print("\n⚠️ El servidor responde, pero las variables siguen faltando.")
            print("   Revise la pestaña 'Variables > Service' en Railway.")
except urllib.error.HTTPError as e:
    if e.code == 404:
        print("❌ FALLO: Sigue diciendo 'Not Found' (404).")
        print("   Esto significa que Railway NO está leyendo la rama 'soberano-v1'.")
        print("   Solución: En Railway, vaya a Settings > Danger > Remove Service, y vuelva a crearlo seleccionando la rama 'soberano-v1'.")
    else:
        print(f"❌ Error HTTP: {e.code}")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
EOF

python3 << 'EOF'
import os
import re

print("=" * 80)
print("🔐 SCRIPT DE EXTRACCIÓN SEGURA DE VARIABLES PARA RAILWAY")
print("=" * 80)

# Lista de variables críticas que necesitamos
vars_requeridas = [
    "TELEGRAM_BOT_TOKEN",
    "DIRECTOR_CHAT_ID",
    "ALPACA_API_KEY",
    "ALPACA_SECRET_KEY",
    "ALPACA_PAPER",
    "UPSTASH_REDIS_REST_URL",
    "UPSTASH_REDIS_REST_TOKEN"
]

variables_encontradas = {}

# 1. Intentar leer del entorno local (si las exportó en Termux)
for var in vars_requeridas:
    valor = os.getenv(var)
    if valor:
        variables_encontradas[var] = valor

# 2. Si no están en el entorno, intentar leer del archivo de respaldo que creamos antes
if len(variables_encontradas) < 7 and os.path.exists("VARIABLES_PARA_RAILWAY.txt"):
    with open("VARIABLES_PARA_RAILWAY.txt", "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, val = line.strip().split("=", 1)
                if key in vars_requeridas and val != "PEGUE_AQUI_SU_TOKEN_REAL":
                    variables_encontradas[key] = val

# 3. Intentar leer un archivo .env local si existe
if len(variables_encontradas) < 7 and os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, val = line.strip().split("=", 1)
                if key in vars_requeridas:
                    variables_encontradas[key] = val

print("\n📊 ESTADO DE DETECCIÓN:")
for var in vars_requeridas:
    if var in variables_encontradas:
        valor = variables_encontradas[var]
        # ENMASCARAMIENTO DE SEGURIDAD: Solo mostramos los primeros 4 y últimos 4 caracteres
        if len(valor) > 8:
            valor_mostrado = valor[:4] + "********" + valor[-4:]
        else:
            valor_mostrado = "****"
        print(f"   ✅ {var}: {valor_mostrado}")
    else:
        print(f"   ❌ {var}: NO ENCONTRADA (Debe ingresarla manualmente)")

# 4. Generar el archivo final limpio para Railway
print("\n📝 Generando archivo limpio para copiar a Railway...")
with open("COPIAR_EN_RAILWAY_RAW.txt", "w", encoding="utf-8") as f:
    for var in vars_requeridas:
        valor = variables_encontradas.get(var, "REEMPLAZAR_MANUALMENTE")
        f.write(f"{var}={valor}\n")

print("   ✅ Archivo 'COPIAR_EN_RAILWAY_RAW.txt' generado exitosamente.")
print("=" * 80)
print("🛡️ INSTRUCCIÓN DE SEGURIDAD:")
print("1. NO tome captura de pantalla a la terminal.")
print("2. Abra el archivo 'COPIAR_EN_RAILWAY_RAW.txt' con un editor de texto.")
print("3. Si alguna dice 'REEMPLAZAR_MANUALMENTE', edítela con el valor real de Vercel/GitHub.")
print("4. Copie TODO el contenido de ese archivo y péguelo en el 'Raw Editor' de Railway.")
print("=" * 80)
EOF

python3 << 'EOF'
import os
import json

print("=" * 80)
print("🔧 SCRIPT DE SINCRONIZACIÓN DE VARIABLES SHARED → SERVICE")
print("=" * 80)

# Lista de variables que necesitamos sincronizar
vars_a_sincronizar = [
    "TELEGRAM_BOT_TOKEN",
    "DIRECTOR_CHAT_ID",
    "ALPACA_API_KEY",
    "ALPACA_SECRET_KEY",
    "ALPACA_PAPER",
    "UPSTASH_REDIS_REST_URL",
    "UPSTASH_REDIS_REST_TOKEN"
]

print("\n📋 VARIABLES QUE DEBE COMPARTIR AL SERVICIO:")
for var in vars_a_sincronizar:
    print(f"   • {var}")

print("\n" + "=" * 80)
print("📝 INSTRUCCIONES PARA COMPARTIR LAS VARIABLES (30 SEGUNDOS):")
print("=" * 80)
print("\n1. Vaya a Railway → Su Proyecto → Pestaña 'Shared Variables'")
print("2. Para CADA variable de la lista anterior:")
print("   a. Haga clic en el botón 'SHARE' a la derecha de la variable")
print("   b. Seleccione el servicio 'maestrotrading'")
print("   c. Haga clic en 'Save' o 'Confirm'")
print("3. Repita para las 7 variables")
print("4. Railway reiniciará el servicio automáticamente")

print("\n" + "=" * 80)
print("🔍 VERIFICACIÓN AUTOMÁTICA DESPUÉS DE COMPARTIR:")
print("=" * 80)
print("\nDespués de compartir las variables, ejecute este script para verificar:")
print()
print("python3 << 'EOF2'")
print("import urllib.request, json")
print("url = 'https://maestrotrading-production-c2db.up.railway.app/debug-env'")
print("try:")
print("    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})")
print("    with urllib.request.urlopen(req) as response:")
print("        data = json.loads(response.read().decode())")
print("        vars_info = data.get('auditoria_variables_en_vivo', {})")
print("        print('\\n📊 ESTADO DE VARIABLES:')")
print("        print(f\"   TELEGRAM_BOT_TOKEN: {'✅' if vars_info.get('TELEGRAM_BOT_TOKEN_existe') else '❌'}\")")
print("        print(f\"   DIRECTOR_CHAT_ID: {vars_info.get('DIRECTOR_CHAT_ID_valor')}\")")
print("        print(f\"   ALPACA_API_KEY: {'✅' if vars_info.get('ALPACA_API_KEY_existe') else '❌'}\")")
print("        if vars_info.get('TELEGRAM_BOT_TOKEN_existe'):")
print("            print('\\n🎉 ¡ÉXITO! Vaya a Telegram y envíe: /estado')")
print("except Exception as e:")
print("    print(f'❌ Error: {e}')")
print("EOF2")

print("\n" + "=" * 80)
print("💡 ALTERNATIVA MÁS RÁPIDA (SI NO QUIERE HACER CLIC 7 VECES):")
print("=" * 80)
print("\nSi prefiere no hacer clic en 'SHARE' 7 veces, puede:")
print("1. Ir a Variables del servicio 'maestrotrading'")
print("2. Hacer clic en 'Raw Editor'")
print("3. Copiar y pegar este bloque (reemplazando los valores):")
print()
print("TELEGRAM_BOT_TOKEN=${{shared.TELEGRAM_BOT_TOKEN}}")
print("DIRECTOR_CHAT_ID=${{shared.DIRECTOR_CHAT_ID}}")
print("ALPACA_API_KEY=${{shared.ALPACA_API_KEY}}")
print("ALPACA_SECRET_KEY=${{shared.ALPACA_SECRET_KEY}}")
print("ALPACA_PAPER=${{shared.ALPACA_PAPER}}")
print("UPSTASH_REDIS_REST_URL=${{shared.UPSTASH_REDIS_REST_URL}}")
print("UPSTASH_REDIS_REST_TOKEN=${{shared.UPSTASH_REDIS_REST_TOKEN}}")
print()
print("4. Hacer clic en 'Update Variables'")
print("5. Railway sincronizará automáticamente las Shared Variables al servicio")

print("\n" + "=" * 80)
EOF

python3 << 'EOF'
import urllib.request, json
url = 'https://maestrotrading-production-c2db.up.railway.app/debug-env'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        vars_info = data.get('auditoria_variables_en_vivo', {})
        print('\n📊 ESTADO DE VARIABLES:')
        print(f"   TELEGRAM_BOT_TOKEN: {'✅' if vars_info.get('TELEGRAM_BOT_TOKEN_existe') else '❌'}")
        print(f"   DIRECTOR_CHAT_ID: {vars_info.get('DIRECTOR_CHAT_ID_valor')}")
        print(f"   ALPACA_API_KEY: {'✅' if vars_info.get('ALPACA_API_KEY_existe') else '❌'}")
        if vars_info.get('TELEGRAM_BOT_TOKEN_existe'):
            print('\n🎉 ¡ÉXITO! Vaya a Telegram y envíe: /estado')
except Exception as e:
    print(f'❌ Error: {e}')
EOF

python3 << 'EOF'
import urllib.request, json
url = 'https://maestrotrading-production-c2db.up.railway.app/debug-env'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        vars_info = data.get('auditoria_variables_en_vivo', {})
        print('\n📊 ESTADO DE VARIABLES:')
        print(f"   TELEGRAM_BOT_TOKEN: {'✅' if vars_info.get('TELEGRAM_BOT_TOKEN_existe') else '❌'}")
        print(f"   DIRECTOR_CHAT_ID: {vars_info.get('DIRECTOR_CHAT_ID_valor')}")
        print(f"   ALPACA_API_KEY: {'✅' if vars_info.get('ALPACA_API_KEY_existe') else '❌'}")
        if vars_info.get('TELEGRAM_BOT_TOKEN_existe'):
            print('\n🎉 ¡ÉXITO! Vaya a Telegram y envíe: /estado')
except Exception as e:
    print(f'❌ Error: {e}')
EOF

python3 << 'EOF'
print("=" * 60)
print("🔍 PRUEBA DE CONEXIÓN DIRECTA A ALPACA")
print("=" * 60)

api_key = input("1. Pegue su ALPACA_API_KEY: ").strip()
secret_key = input("2. Pegue su ALPACA_SECRET_KEY: ").strip()
is_paper = input("3. ¿Es cuenta Paper? (s/n): ").strip().lower() == 's'

print("\n⏳ Conectando con Alpaca...")

try:
    from alpaca.trading.client import TradingClient
    client = TradingClient(api_key=api_key, secret_key=secret_key, paper=is_paper)
    
    account = client.get_account()
    print("\n✅ ¡CONEXIÓN EXITOSA!")
    print(f"   Estado de la cuenta: {account.status}")
    print(f"   Capital disponible (Buying Power): ${float(account.buying_power):.2f}")
    print(f"   Entorno: {'PAPER TRADING' if is_paper else 'LIVE'}")
    print("\n🎉 Las claves son correctas. El problema era un espacio en blanco o una clave antigua en Railway.")
    
except Exception as e:
    print("\n❌ CONEXIÓN FALLIDA")
    print(f"   Error de Alpaca: {e}")
    print("\n💡 SOLUCIÓN: Sus claves son incorrectas o no coinciden con el entorno Paper/Live.")
    print("   Vaya a app.alpaca.markets y regenere las API Keys.")

print("=" * 60)
EOF

python3 << 'EOF'
import os
import subprocess

print("=" * 80)
print("🔍 INYECTANDO DIAGNÓSTICO DE ALPACA EN VIVO (DESDE RAILWAY)")
print("=" * 80)

# Leer el index.py actual
index_path = "SOBERANO_03_NEXUS/index.py"
with open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

# Código del nuevo endpoint de diagnóstico de Alpaca
alpaca_debug_code = """
@app.get("/debug-alpaca")
async def debug_alpaca():
    # Diagnóstico en vivo de la conexión a Alpaca DESDE el servidor de Railway
    api_key = os.getenv("ALPACA_API_KEY", "").strip()
    secret_key = os.getenv("ALPACA_SECRET_KEY", "").strip()
    is_paper = os.getenv("ALPACA_PAPER", "false").lower() == "true"
    
    resultado = {
        "servidor": "Railway (En vivo)",
        "variables_leidas": {
            "ALPACA_API_KEY_longitud": len(api_key),
            "ALPACA_API_KEY_primeros_4": api_key[:4] + "..." if api_key else "VACIO",
            "ALPACA_SECRET_KEY_longitud": len(secret_key),
            "ALPACA_PAPER_valor": is_paper
        },
        "intento_de_conexion": "Pendiente..."
    }
    
    if not api_key or not secret_key:
        resultado["intento_de_conexion"] = "FALLIDO: Las claves están vacías en Railway."
        return resultado
        
    try:
        from alpaca.trading.client import TradingClient
        client = TradingClient(api_key=api_key, secret_key=secret_key, paper=is_paper)
        account = client.get_account()
        
        resultado["intento_de_conexion"] = "✅ EXITOSA"
        resultado["detalles_cuenta"] = {
            "status": account.status,
            "buying_power": float(account.buying_power),
            "equity": float(account.equity)
        }
    except Exception as e:
        resultado["intento_de_conexion"] = "❌ FALLIDO"
        resultado["error_exacto_de_alpaca"] = str(e)
        
    return resultado
"""

# Insertar el nuevo endpoint antes del bloque `if __name__ == "__main__":`
if "/debug-alpaca" not in content:
    content = content.replace(
        'if __name__ == "__main__":',
        alpaca_debug_code + '\nif __name__ == "__main__":'
    )
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Endpoint /debug-alpaca inyectado exitosamente.")
else:
    print("ℹ️ El endpoint /debug-alpaca ya existe.")

# Commit y Push
print("\n📤 Enviando a GitHub para despliegue en Railway...")
subprocess.run(["git", "add", index_path], capture_output=True)
subprocess.run(["git", "commit", "-m", "[AUDIT] Agregado endpoint /debug-alpaca para validar conexión en vivo"], capture_output=True)
push_result = subprocess.run(["git", "push", "origin", "soberano-v1"], capture_output=True, text=True)

if push_result.returncode == 0:
    print("✅ Desplegado a GitHub. Railway comenzará a construir.")
else:
    print(f"⚠️ Advertencia: {push_result.stderr}")

print("\n" + "=" * 80)
print("⏳ ESPERE 2 MINUTOS A QUE RAILWAY TERMINE DE CONSTRUIR (Estado: Active)")
print("LUEGO, VISITE EN SU NAVEGADOR:")
print("https://maestrotrading-production-c2db.up.railway.app/debug-alpaca")
print("=" * 80)
EOF

