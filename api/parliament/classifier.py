# === MAESTRO-NEXUS: CLASIFICADOR DE INTENCIÓN ===
# ID: api/parliament/classifier.py | ESTADO: MODULARIZADO
# FECHA: 2026-06-30 | Decide qué departamento responde según el mensaje.

import re

# Palabras clave por departamento
DEPARTMENTS = {
    "mercado": {
        "keywords": ["inversión", "invertir", "trading", "acciones", "mercado", "precio",
                     "compra", "venta", "ticker", "forex", "cripto", "riesgo", "rentabilidad",
                     "capital", "ganancia", "pérdida", "alza", "baja", "volatilidad"],
        "role": "estratega"
    },
    "auditoria": {
        "keywords": ["código", "bug", "error", "github", "deploy", "router", "index",
                     "python", "función", "script", "vercel", "redis", "api", "token",
                     "commit", "push", "pull", "merge", "rama", "branch"],
        "role": "auditor"
    },
    "documentacion": {
        "keywords": ["acta", "historial", "bitácora", "documento", "constitución",
                     "qué decidimos", "último debate", "memoria", "trazabilidad",
                     "registro", "anterior", "pasado", "ayer", "semana"],
        "role": "guardian"
    },
    "gobernanza": {
        "keywords": ["arquitectura", "parlamento", "roles", "constitución",
                     "cambio grande", "estrategia", "fase", "módulo", "debate",
                     "decisión", "votar", "aprobar", "vetar"],
        "role": "gerente"
    }
}

def classify_intent(text: str) -> dict:
    """Clasifica el mensaje y devuelve el departamento y rol."""
    text_lower = text.lower()
    
    scores = {}
    for dept, config in DEPARTMENTS.items():
        score = 0
        for keyword in config["keywords"]:
            if keyword in text_lower:
                score += 1
        if score > 0:
            scores[dept] = score
    
    if scores:
        best = max(scores, key=scores.get)
        return {"department": best, "role": DEPARTMENTS[best]["role"], "confidence": scores[best]}
    
    return {"department": "general", "role": "gerente", "confidence": 0}
