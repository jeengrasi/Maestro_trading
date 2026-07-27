def classify_intent(text: str) -> dict:
    text_lower = text.lower()
    trading_keywords = ["comprar", "vender", "btc", "eth", "alpaca", "trading", "invertir", "acción", "acciones"]
    
    if any(k in text_lower for k in trading_keywords):
        return {"role": "estratega", "department": "trading", "confidence": 0.9}
    
    return {"role": "gerente", "department": "debate", "confidence": 0.8}
