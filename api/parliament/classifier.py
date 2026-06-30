import re

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
                     "commit", "push", "pull", "merge", "rama", "branch", "revisa"],
        "role": "auditor"
    },
    "documentacion": {
        "keywords": ["acta", "historial", "bitácora", "documento", "constitución",
                     "memoria", "trazabilidad", "registro", "anterior", "pasado"],
        "role": "guardian"
    },
    "gobernanza": {
        "keywords": ["arquitectura", "parlamento", "roles", "fase", "módulo", "debate",
                     "decisión", "votar", "aprobar", "vetar"],
        "role": "gerente"
    }
}

def classify_intent(text: str) -> dict:
    text_lower = text.lower()
    scores = {}
    for dept, config in DEPARTMENTS.items():
        score = sum(1 for kw in config["keywords"] if kw in text_lower)
        if score > 0:
            scores[dept] = score
    
    if not scores:
        return {"department": "general", "role": "gerente", "confidence": 0}
    
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_dept, best_score = sorted_scores[0]
    second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0
    
    if best_score > second_score:
        return {"department": best_dept, "role": DEPARTMENTS[best_dept]["role"], "confidence": best_score}
    
    return {"department": "general", "role": "gerente", "confidence": 0}
