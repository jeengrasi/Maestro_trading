# ================================================
# MAESTRO-NEXUS | SCHEDULER V2.0
# ================================================
# ID: api/core/scheduler.py
# COMMIT: scheduler_v2.0_bitacora
# FECHA: 2026-07-05
# AUTOR: Gerente (DeepSeek)
# ESTADO: ✅ COMPLETO
# ================================================
# CAMBIOS vs V1.0:
# - Tarea de Bitácora cada 24h
# - Contador de fallos (alerta en 3 fallos)
# - Logs y backups integrados
# ================================================

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, Callable, Awaitable

logger = logging.getLogger(__name__)

# Contador global de fallos de Bitácora
FALLOS_BITACORA = 0

# ================================================
# SECCIÓN 1: DEFINICIÓN DEL SCHEDULER
# ================================================

class Scheduler:
    """Motor de tareas programadas."""
    
    def __init__(self, redis_client, alpaca_client=None, github_repo=None):
        self.redis = redis_client
        self.alpaca = alpaca_client
        self.github = github_repo
        self.tasks = {}
        self.running = False
        self._loop_task = None
        
    def register_task(self, name: str, task_func: Callable[[], Awaitable[Any]], interval: int):
        """
        Registra una tarea en el scheduler.
        
        Args:
            name: Nombre único de la tarea
            task_func: Función asíncrona a ejecutar
            interval: Intervalo en segundos entre ejecuciones
        """
        self.tasks[name] = {
            "func": task_func,
            "interval": interval,
            "last_run": None,
            "status": "registered"
        }
        logger.info(f"📋 Tarea registrada: {name} (intervalo: {interval}s)")
        
    async def _run_task(self, name: str, task_info: dict):
        """Ejecuta una tarea individual con manejo de errores."""
        global FALLOS_BITACORA
        
        try:
            logger.info(f"🔄 Ejecutando tarea: {name}")
            start_time = datetime.now()
            
            # Ejecutar la tarea
            result = await task_info["func"]()
            
            # Si es la tarea de Bitácora, manejar el contador de fallos
            if name == "bitacora":
                if isinstance(result, tuple) and len(result) >= 2:
                    exito, msg = result[0], result[1]
                    if exito:
                        FALLOS_BITACORA = 0
                        logger.info(f"✅ Tarea {name} completada: {msg}")
                    else:
                        FALLOS_BITACORA += 1
                        logger.warning(f"⚠️ Falla {FALLOS_BITACORA}/3 en {name}: {msg}")
                        if FALLOS_BITACORA >= 3:
                            logger.critical(f"🔥 ALERTA: 3 fallos consecutivos en {name}!")
                            # Aquí se podría enviar alerta a Telegram
            
            # Registrar en Redis
            if self.redis:
                key = f"scheduler:task:{name}:last_result"
                self.redis.set(key, json.dumps({
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "result": str(result)[:500]
                }))
                self.redis.expire(key, 86400)
            
            # Actualizar estado
            task_info["last_run"] = datetime.now()
            task_info["status"] = "success"
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Tarea {name} completada en {elapsed:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Error en tarea {name}: {e}")
            task_info["status"] = "error"
            task_info["last_error"] = str(e)
            
            # Si es Bitácora, incrementar contador de fallos
            if name == "bitacora":
                FALLOS_BITACORA += 1
                logger.warning(f"⚠️ Falla {FALLOS_BITACORA}/3 en {name}: {e}")
                if FALLOS_BITACORA >= 3:
                    logger.critical(f"🔥 ALERTA: 3 fallos consecutivos en {name}!")
            
            # Registrar error en Redis
            if self.redis:
                key = f"scheduler:task:{name}:last_error"
                self.redis.set(key, json.dumps({
                    "status": "error",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e)
                }))
                self.redis.expire(key, 86400)
    
    async def _scheduler_loop(self):
        """Bucle principal del scheduler."""
        logger.info("🚀 Scheduler iniciado")
        self.running = True
        
        while self.running:
            current_time = datetime.now()
            
            for name, task_info in self.tasks.items():
                if task_info["last_run"] is None:
                    should_run = True
                else:
                    elapsed = (current_time - task_info["last_run"]).total_seconds()
                    should_run = elapsed >= task_info["interval"]
                
                if should_run:
                    asyncio.create_task(self._run_task(name, task_info))
            
            await asyncio.sleep(5)
    
    async def start(self):
        """Inicia el scheduler."""
        if self._loop_task is None:
            self._loop_task = asyncio.create_task(self._scheduler_loop())
            logger.info("✅ Scheduler en ejecución")
        else:
            logger.warning("⚠️ Scheduler ya está en ejecución")
    
    async def stop(self):
        """Detiene el scheduler."""
        self.running = False
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
            self._loop_task = None
            logger.info("🛑 Scheduler detenido")
    
    def get_status(self) -> dict:
        """Obtiene el estado de todas las tareas."""
        status = {
            "running": self.running,
            "tasks": {}
        }
        for name, info in self.tasks.items():
            status["tasks"][name] = {
                "interval": info["interval"],
                "last_run": info["last_run"].isoformat() if info["last_run"] else None,
                "status": info["status"]
            }
        return status

# ================================================
# SECCIÓN 2: TAREAS PREDEFINIDAS
# ================================================

async def task_health_check(redis_client, alpaca_client) -> dict:
    """Verifica el estado de los servicios críticos."""
    results = {}
    
    try:
        ping = redis_client.ping()
        results["redis"] = "ok" if ping else "degraded"
    except Exception as e:
        results["redis"] = f"error: {str(e)}"
    
    try:
        if alpaca_client:
            account = alpaca_client.get_account()
            results["alpaca"] = "ok"
            results["equity"] = float(account.equity)
        else:
            results["alpaca"] = "not_configured"
    except Exception as e:
        results["alpaca"] = f"error: {str(e)}"
    
    return results

async def task_cleanup_redis(redis_client) -> dict:
    """Limpia claves expiradas y memoria antigua en Redis."""
    results = {}
    
    try:
        keys = redis_client.keys("scheduler:task:*:last_result")
        deleted = 0
        for key in keys:
            ttl = redis_client.ttl(key)
            if ttl < 0 and ttl != -1:
                redis_client.delete(key)
                deleted += 1
        
        results["deleted_expired"] = deleted
        results["status"] = "ok"
    except Exception as e:
        results["status"] = f"error: {str(e)}"
    
    return results

async def task_bitacora() -> tuple:
    """
    Tarea de actualización de Bitácora.
    Ejecuta el generador y retorna (exito, mensaje).
    """
    try:
        from api.core.generar_bitacora import generar_bitacora
        return generar_bitacora()
    except Exception as e:
        return False, str(e)

# ================================================
# SECCIÓN 3: FUNCIÓN DE INICIALIZACIÓN
# ================================================

_scheduler_instance = None

def get_scheduler(redis_client=None, alpaca_client=None, github_repo=None):
    """Obtiene o crea una instancia del scheduler (Singleton)."""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = Scheduler(redis_client, alpaca_client, github_repo)
    return _scheduler_instance

def init_scheduler(redis_client, alpaca_client=None, github_repo=None):
    """Inicializa y registra las tareas por defecto."""
    scheduler = get_scheduler(redis_client, alpaca_client, github_repo)
    
    # Registrar tareas
    scheduler.register_task(
        "health_check",
        lambda: task_health_check(redis_client, alpaca_client),
        interval=60  # Cada minuto
    )
    
    scheduler.register_task(
        "cleanup_redis",
        lambda: task_cleanup_redis(redis_client),
        interval=3600  # Cada hora
    )
    
    # ================================================
    # NUEVA TAREA: BITÁCORA (cada 24 horas)
    # ================================================
    scheduler.register_task(
        "bitacora",
        task_bitacora,
        interval=86400  # 24 horas
    )
    
    return scheduler

# ================================================
# FIN DEL ARCHIVO
# ================================================
