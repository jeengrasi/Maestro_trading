#!/bin/bash
source ~/.nexus_secrets

DEBATE=$(curl -s "$UPSTASH_REDIS_REST_URL/get/memory:last_debate" -H "Authorization: Bearer $UPSTASH_REDIS_REST_TOKEN")

if [ -z "$DEBATE" ] || [ "$DEBATE" = "null" ]; then
    echo "❌ No hay debate en Redis."
    exit 1
fi

TEMA=$(echo "$DEBATE" | python3 -c "import sys,json; print(json.loads(json.load(sys.stdin)['result'])['tema'])")
FECHA=$(echo "$DEBATE" | python3 -c "import sys,json; print(json.loads(json.load(sys.stdin)['result'])['fecha'])")
RESPUESTA=$(echo "$DEBATE" | python3 -c "import sys,json; print(json.loads(json.load(sys.stdin)['result'])['respuesta'])")

ACTA_ID="NEXUS-ACT-$(date +%Y%m%d-%H%M)"
ACTA="# Acta de Debate

**ID:** ${ACTA_ID}
**Fecha:** ${FECHA}
**Tema:** ${TEMA}

${RESPUESTA}
"

ACTA_B64=$(echo -n "$ACTA" | base64)
curl -s -X PUT "https://api.github.com/repos/jeengrasi/Maestro_trading/contents/docs/actas/${ACTA_ID}.md" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Acta ${ACTA_ID}\",\"content\":\"${ACTA_B64}\",\"branch\":\"main\"}" > /dev/null

echo "✅ Acta ${ACTA_ID} guardada en GitHub."
