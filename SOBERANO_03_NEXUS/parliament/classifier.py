def classify_intent(text: str) -> dict:
    text_lower = text.lower()
    if any(k in text_lower for k in ["comprar", "vender", "btc", "eth", "alpaca", "trading"]):
        return {"role": "trader", "department": "trading", "confidence": 0.9}
    return {"role": "gerente", "department": "debate", "confidence": 0.8}
