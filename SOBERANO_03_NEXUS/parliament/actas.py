async def generate_acta(prompt: str, decision: str, role: str) -> str:
    return f"Acta Oficial - Rol: {role} | Decisión: {decision}"

async def save_acta_to_github(content: str, issue_id: str) -> str:
    return f"Acta guardada en GitHub (ID: {issue_id})"
