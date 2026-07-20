import os
import redis
import json
from datetime import datetime

# Conectar a Redis
REDIS_URL = os.getenv("UPSTASH_REDIS_REST_URL")
REDIS_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

if not REDIS_URL:
    print("❌ Error: UPSTASH_REDIS_REST_URL no configurada")
    exit(1)

r = redis.from_url(f"{REDIS_URL}?password={REDIS_TOKEN}")

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

for doc in documentos:
    path = os.path.join(BASE, doc)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        # Guardar en Redis
        key = f"doc:{doc.replace('/', ':')}"
        r.hset(key, mapping={
            "contenido": contenido[:5000],
            "ruta": doc,
            "fecha_index": datetime.now().isoformat()
        })
        print(f"✅ Indexado: {doc}")
    else:
        print(f"⚠️ No encontrado: {doc}")

print("✅ Indexación completada.")
