from .core import call_ia

async def get_manager_recommendation(message: str, responses: dict) -> str:
    context = "Debate Parlamentario Nexus IA:\n\n"
    for role, data in responses.items():
        context += f"{data['role']}:\n{data['response']}\n\n"
    if len(context) > 8000:
        context = context[:8000] + "\n\n[Contexto truncado]"
    prompt = f"{context}\nComo Gerente General, emite tu recomendación final."
    return await call_ia("gerente", prompt)
