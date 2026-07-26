import os

PARLIAMENT_STACK = {
    "gerente": "DeepSeek / Gemini",
    "analista": "Groq / NVIDIA",
    "auditor": "EAD Controller"
}

def sanitize_prompt(prompt: str) -> str:
    return prompt.strip()

async def call_ia(role: str, message: str) -> str:
    return f"[{role.upper()}] Procesado mensaje: {message[:30]}..."
