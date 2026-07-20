import os
import redis
import json
from datetime import datetime

# Leer variables directamente del archivo
def get_secret(key):
    try:
        with open(os.path.expanduser("~/.nexus_secrets"), "r") as f:
            for line in f:
                if line.startswith(key + "="):
                    return line.strip().split("=", 1)[1].strip('"')
    except:
        pass
    return None

REDIS_URL = get_secret("UPSTASH_REDIS_REST_URL")
REDIS_TOKEN = get_secret("UPSTASH_REDIS_REST_TOKEN")

if not REDIS_URL:
    print("❌ Error: No se pudo leer UPSTASH_REDIS_REST_URL")
    exit(1)

# Convertir https:// a redis://
if REDIS_URL.startswith("https://"):
    REDIS_URL = REDIS_URL.replace("https://", "redis://", 1)
elif REDIS_URL.startswith("http://"):
    REDIS_URL = REDIS_URL.replace("http://", "redis://", 1)

print(f"📋 Conectando a Redis: {REDIS_URL[:30]}...")

try:
    r = redis.from_url(f"{REDIS_URL}?password={REDIS_TOKEN}")
    r.ping()
    print("✅ Conexión a Redis exitosa")
except Exception as e:
    print(f"❌ Error conectando a Redis: {e}")
    exit(1)

# Ruta base
BASE = os.path.expanduser("~/Maestro_trading")

# Documentos a indexar
documentos = [
    "00-GOBIERNO/DOCS/constitucion.md",
    "00-GOBIERNO/DOCS/roles.md",
    "00-GOBIERNO/DOCS/NEXUS_MANIFEST.json",
    "01-MEMORIA/DOCS/actas/NEXUS-DEB-20260630-0214.md",
    "02-SISTEMA/DOCS/estado_actual.md",
    "02-SISTEMA/DOCS/proveedores.md",
    "04-REGISTROS/DOCS/bitacora.md",
    "05-DOCUMENTACION/DOCS/00_INDICE.md",
]

indexados = 0
for doc in documentos:
    path = os.path.join(BASE, doc)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        key = f"doc:{doc.replace('/', ':')}"
        r.hset(key, mapping={
            "contenido": contenido[:5000],
            "ruta": doc,
            "fecha_index": datetime.now().isoformat()
        })
        print(f"✅ Indexado: {doc}")
        indexados += 1
    else:
        print(f"⚠️ No encontrado: {doc}")

print(f"✅ Indexación completada. {indexados} documentos indexados.")
