import asyncio
from .core import PARLIAMENT_STACK, call_ia

async def handle_parliament_debate(message: str) -> dict:
    results = {}
    roles_to_call = [r for r in PARLIAMENT_STACK.keys() if r not in ("gerente", "secretario")]
    tasks = [call_ia(role, message) for role in roles_to_call]
    responses = await asyncio.gather(*tasks)
    for role, response in zip(roles_to_call, responses):
        results[role] = {"role": PARLIAMENT_STACK[role]["role"], "model": PARLIAMENT_STACK[role]["model"], "response": response}
    return results
