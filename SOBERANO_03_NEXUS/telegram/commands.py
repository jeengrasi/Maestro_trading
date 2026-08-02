# ==============================================================================
# ARCHIVO: commands.py
# MODULO: telegram
# DEPARTAMENTO: 03 - NEXUS (Telecomunicaciones)
# SISTEMA: MAESTRO-NEXUS
# ROL: Procesador de Comandos Telegram
# MISIÓN: Manejar comandos del Director (/autorizar, /pausar, /estado, etc.)
#         leyendo/escribiendo en Redis y consultando Alpaca.
# DEBERES: Cumplir con la Constitución, verificar chat_id, responder en <5 seg.
# PROHIBICIONES: Ejecutar trading directamente, modificar archivos de gobierno.
# ULTIMA MODIFICACION: 2026-08-01
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: Constitución v7.1 (Art. 1, 14), Fase 1.2
# ==============================================================================

import os
import logging
from datetime import datetime, timedelta
from alpaca.trading.client import TradingClient
from upstash_redis import Redis
from SOBERANO_03_NEXUS.config import Config
from SOBERANO_03_NEXUS.telegram.formatters import (
    format_estado, format_posiciones_abiertas, format_historial
)

logger = logging.getLogger(__name__)

class CommandProcessor:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.config = Config()
        # Usar URL explícita de Paper Trading para evitar problemas
        if self.config.ALPACA_PAPER:
            self.trading_client = TradingClient(
                self.config.ALPACA_API_KEY,
                self.config.ALPACA_SECRET_KEY,
                paper=True,
                url_override="https://paper-api.alpaca.markets"
            )
        else:
            self.trading_client = TradingClient(
                self.config.ALPACA_API_KEY,
                self.config.ALPACA_SECRET_KEY,
                paper=False
            )
        self.director_chat_id = int(os.getenv("DIRECTOR_CHAT_ID", "0"))
    
    def verificar_autorizacion(self, chat_id: int) -> bool:
        """Verifica que el chat_id sea del Director."""
        return chat_id == self.director_chat_id
    
    def procesar_comando(self, comando: str, args: list = None) -> str:
        """Procesa un comando y retorna la respuesta."""
        if args is None:
            args = []
        
        try:
            if comando == "/autorizar":
                return self._comando_autorizar(args)
            elif comando == "/pausar":
                return self._comando_pausar()
            elif comando == "/estado":
                return self._comando_estado()
            elif comando == "/posiciones":
                return self._comando_posiciones()
            elif comando == "/historial":
                return self._comando_historial()
            else:
                return "❓ Comando no reconocido. Use /estado para ver opciones."
        except Exception as e:
            logger.error(f"Error procesando comando {comando}: {e}")
            return f"❌ Error al procesar comando: {str(e)[:100]}"
    
    def _comando_autorizar(self, args: list) -> str:
        """Activa AUTO_EJECUCION_TEMP con TTL."""
        try:
            horas = 4  # Default
            if args and args[0].isdigit():
                horas = int(args[0])
            
            ttl_segundos = horas * 3600
            self.redis.set("AUTO_EJECUCION_TEMP", "true", ex=ttl_segundos)
            
            tiempo_expiracion = datetime.now() + timedelta(hours=horas)
            return f"✅ AUTORIZADO por {horas} horas.\nVálido hasta: {tiempo_expiracion.strftime('%H:%M EST')}"
        except Exception as e:
            return f"❌ Error al autorizar: {str(e)[:100]}"
    
    def _comando_pausar(self) -> str:
        """Desactiva AUTO_EJECUCION_TEMP."""
        try:
            self.redis.delete("AUTO_EJECUCION_TEMP")
            return "⏸️ Modo trading PAUSADO. El bot no ejecutará nuevas operaciones."
        except Exception as e:
            return f"❌ Error al pausar: {str(e)[:100]}"
    
    def _comando_estado(self) -> str:
        """Muestra estado completo del sistema."""
        try:
            account = self.trading_client.get_account()
            capital_total = float(account.equity)
            buying_power = float(account.buying_power)
            
            # Calcular P&L diario (simplificado)
            pnl_diario = float(account.equity) - float(account.last_equity)
            
            # Posiciones abiertas
            posiciones = self.trading_client.get_all_positions()
            num_posiciones = len(posiciones)
            
            # Drawdown (simplificado)
            drawdown_pct = 0.0
            if float(account.last_equity) > 0:
                drawdown_pct = ((float(account.last_equity) - capital_total) / float(account.last_equity)) * 100
            
            # Circuit Breaker
            cb_state = self.redis.get("circuit_breaker:active")
            circuit_breaker_activo = cb_state and cb_state.decode() == "true"
            
            # Auto Ejecución
            auto_state = self.redis.get("AUTO_EJECUCION_TEMP")
            auto_ejecucion = auto_state and auto_state.decode().lower() == "true"
            
            # Tiempo restante
            tiempo_restante = None
            if auto_ejecucion:
                ttl = self.redis.ttl("AUTO_EJECUCION_TEMP")
                if ttl > 0:
                    horas = ttl // 3600
                    minutos = (ttl % 3600) // 60
                    tiempo_restante = f"{horas}h {minutos}m"
            
            return format_estado(
                capital_total=capital_total,
                buying_power=buying_power,
                pnl_diario=pnl_diario,
                posiciones_abiertas=num_posiciones,
                drawdown_pct=drawdown_pct,
                circuit_breaker_activo=circuit_breaker_activo,
                auto_ejecucion=auto_ejecucion,
                tiempo_restante=tiempo_restante
            )
        except Exception as e:
            return f"❌ Error al obtener estado: {str(e)[:100]}"
    
    def _comando_posiciones(self) -> str:
        """Lista posiciones abiertas."""
        try:
            posiciones = self.trading_client.get_all_positions()
            
            posiciones_data = []
            for pos in posiciones:
                pnl = float(pos.unrealized_pl)
                pnl_pct = (pnl / (float(pos.avg_entry_price) * float(pos.qty))) * 100 if float(pos.qty) > 0 else 0
                
                posiciones_data.append({
                    "symbol": pos.symbol,
                    "qty": int(pos.qty),
                    "avg_entry_price": float(pos.avg_entry_price),
                    "current_price": float(pos.current_price),
                    "pnl": pnl,
                    "pnl_pct": pnl_pct
                })
            
            return format_posiciones_abiertas(posiciones_data)
        except Exception as e:
            return f"❌ Error al obtener posiciones: {str(e)[:100]}"
    
    def _comando_historial(self) -> str:
        """Muestra historial de operaciones cerradas."""
        try:
            # Consultar actividades de llenado (fills)
            activities = self.trading_client.get_activities()
            
            # Filtrar solo fills (operaciones ejecutadas)
            fills = [act for act in activities if hasattr(act, 'side')]
            
            operaciones = []
            for fill in fills[:10]:
                operaciones.append({
                    "symbol": fill.symbol,
                    "fecha": fill.timestamp.strftime('%Y-%m-%d %H:%M') if hasattr(fill, 'timestamp') else 'N/A',
                    "precio_entrada": float(fill.price),
                    "precio_salida": float(fill.price),  # Simplificado
                    "pnl": 0.0  # Requiere cálculo más complejo
                })
            
            return format_historial(operaciones)
        except Exception as e:
            return f"❌ Error al obtener historial: {str(e)[:100]}"
