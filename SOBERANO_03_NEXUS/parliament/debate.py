async def handle_parliament_debate(message: str) -> dict:
    return {
        "status": "success",
        "debate_result": f"Debate completado para: {message}",
        "consensus": "Aprobado por el Parlamento"
    }
