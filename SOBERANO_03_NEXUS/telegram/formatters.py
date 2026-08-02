# ==============================================================================
# ARCHIVO: formatters.py
# MODULO: telegram
# DEPARTAMENTO: 03 - NEXUS (Telecomunicaciones)
# SISTEMA: MAESTRO-NEXUS
# ROL: Formateador de Mensajes
# MISIÓN: Convertir datos estructurados en mensajes legibles para Telegram usando
#         formato Markdown con emojis como semáforos visuales.
# DEBERES: Cumplir con la Constitución, mantener mensajes escaneables en <5 seg.
# PROHIBICIONES: Enviar mensajes directamente (usa utils.py), tomar decisiones.
# ULTIMA MODIFICACION: 2026-08-01
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: Constitución v7.1 (Art. 14), Fase 1.2
# ==============================================================================

from datetime import datetime

def format_nueva_posicion(symbol: str, cantidad: int, precio_entrada: float,
                          stop_loss: float, take_profit: float, riesgo_pct: float,
                          confianza_ia: float, razon: str) -> str:
    """Formatea mensaje de nueva posición abierta."""
    return f"""🟢 *NUEVA POSICIÓN: COMPRA {symbol}*
━━━━━━━━━━━━━━━━━━━━━━━
*Cantidad:* {cantidad} acciones
*Precio Entrada:* ${precio_entrada:.2f}
*Stop Loss:* ${stop_loss:.2f} (Delegado a Alpaca)
*Take Profit:* ${take_profit:.2f}
*Riesgo Asumido:* {riesgo_pct:.2f}%
*Confianza IA:* {confianza_ia:.0f}%
*Razón:* {razon}
━━━━━━━━━━━━━━━━━━━━━━━
🛡️ Protegido por bracket order"""

def format_cierre_posicion(symbol: str, tipo: str, precio_entrada: float,
                           precio_salida: float, cantidad: int, pnl: float) -> str:
    """Formatea mensaje de cierre de posición (TP o SL)."""
    emoji = "✅" if pnl > 0 else "🛑"
    tipo_texto = "TAKE PROFIT" if pnl > 0 else "STOP LOSS"
    
    return f"""{emoji} *{tipo_texto} EJECUTADO: {symbol}*
━━━━━━━━━━━━━━━━━━━━━━━
*Precio Venta:* ${precio_salida:.2f}
*P&L Realizado:* ${pnl:+.2f}
*Cantidad:* {cantidad} acciones
━━━━━━━━━━━━━━━━━━━━━━━
{'🎉 Operación exitosa' if pnl > 0 else '⚠️ Pérdida controlada dentro de límites'}"""

def format_resumen_diario(capital_total: float, pnl_diario: float, 
                          posiciones_abiertas: int, drawdown_pct: float) -> str:
    """Formatea resumen diario al cierre del mercado."""
    emoji_pnl = "📈" if pnl_diario >= 0 else "📉"
    
    return f"""📊 *RESUMEN DIARIO - {datetime.now().strftime('%Y-%m-%d')}*
━━━━━━━━━━━━━━━━━━━━━━━
{emoji_pnl} *P&L del Día:* ${pnl_diario:+.2f} ({pnl_diario/capital_total*100:+.2f}%)
💰 *Capital Total:* ${capital_total:.2f}
📈 *Posiciones Abiertas:* {posiciones_abiertas}
📉 *Drawdown:* {drawdown_pct:.2f}%
━━━━━━━━━━━━━━━━━━━━━━━
🏁 Mercado cerrado. Sistema en modo vigilancia."""

def format_alerta_critica(tipo: str, mensaje: str) -> str:
    """Formatea alerta crítica (circuit breaker, errores)."""
    return f"""🚨 *ALERTA CRÍTICA: {tipo}*
━━━━━━━━━━━━━━━━━━━━━━━
{mensaje}
━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Requiere atención inmediata del Director."""

def format_estado(capital_total: float, buying_power: float, pnl_diario: float,
                  posiciones_abiertas: int, drawdown_pct: float, 
                  circuit_breaker_activo: bool, auto_ejecucion: bool,
                  tiempo_restante: str = None) -> str:
    """Formatea estado del sistema."""
    cb_emoji = "🔴 ACTIVO" if circuit_breaker_activo else "🟢 INACTIVO"
    ae_emoji = "🟢 AUTORIZADO" if auto_ejecucion else "🔴 PAUSADO"
    
    mensaje = f"""📊 *ESTADO DEL SISTEMA*
━━━━━━━━━━━━━━━━━━━━━━━
💰 *Capital Total:* ${capital_total:.2f}
💵 *Buying Power:* ${buying_power:.2f}
📈 *P&L Diario:* ${pnl_diario:+.2f}
📈 *Posiciones Abiertas:* {posiciones_abiertas}
📉 *Drawdown:* {drawdown_pct:.2f}%
🛡️ *Circuit Breaker:* {cb_emoji}
⚙️ *Ejecución:* {ae_emoji}"""
    
    if auto_ejecucion and tiempo_restante:
        mensaje += f"\n⏰ *Tiempo restante:* {tiempo_restante}"
    
    mensaje += "\n━━━━━━━━━━━━━━━━━━━━━━━"
    return mensaje

def format_posiciones_abiertas(posiciones: list) -> str:
    """Formatea lista de posiciones abiertas."""
    if not posiciones:
        return "📭 No hay posiciones abiertas actualmente."
    
    mensaje = "📈 *POSICIONES ABIERTAS*\n━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    for pos in posiciones:
        emoji_pnl = "📈" if pos['pnl'] >= 0 else "📉"
        mensaje += f"{emoji_pnl} *{pos['symbol']}* | {pos['qty']} acc\n"
        mensaje += f"   Entrada: ${pos['avg_entry_price']:.2f} | Actual: ${pos['current_price']:.2f}\n"
        mensaje += f"   P&L: ${pos['pnl']:+.2f} ({pos['pnl_pct']:+.2f}%)\n\n"
    
    mensaje += "━━━━━━━━━━━━━━━━━━━━━━━"
    return mensaje

def format_historial(operaciones: list) -> str:
    """Formatea historial de operaciones cerradas."""
    if not operaciones:
        return "📭 No hay operaciones cerradas en el historial."
    
    mensaje = "📜 *HISTORIAL DE OPERACIONES*\n━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    for op in operaciones[:10]:  # Máximo 10 para no saturar
        emoji = "✅" if op['pnl'] >= 0 else "🛑"
        mensaje += f"{emoji} *{op['symbol']}* | {op['fecha']}\n"
        mensaje += f"   Entrada: ${op['precio_entrada']:.2f} → Salida: ${op['precio_salida']:.2f}\n"
        mensaje += f"   P&L: ${op['pnl']:+.2f}\n\n"
    
    mensaje += "━━━━━━━━━━━━━━━━━━━━━━━"
    return mensaje
