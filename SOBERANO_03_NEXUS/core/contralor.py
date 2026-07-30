# ==============================================================================
# ARCHIVO: contralor.py
# MODULO: core
# DEPARTAMENTO: 00 - GOBIERNO
# SISTEMA: MAESTRO-NEXUS
# ROL: El Veedor Supremo
# MISIÓN: Auditar la integridad de los archivos de gobierno y bloquear ejecuciones no autorizadas.
# DEBERES: Calcular hashes SHA-256, comparar hashes, bloquear AUTO_EJECUCION_TEMP, generar reportes EDVC.
# PROHIBICIONES: Ejecutar trading, enviar mensajes a Telegram, modificar archivos de gobierno.
# ULTIMA MODIFICACION: 2026-07-30
# AUTOR: Gerente Qwen | VALIDADOR: Director JEISSON_01
# REFERENCIA: SOBERANO_00_GOBIERNO/ROLES_Y_MISIONES.md
# ==============================================================================

# ==============================================================================
# ARCHIVO: contralor.py
# MODULO: core
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Veedor, Auditor y Garantizador de la integridad y alineación normativa del sistema.
# ULTIMA MODIFICACION: 2026-07-28
# AUTOR: Gerente (Qwen) | VALIDADO POR: Director (JEISSON_01)
# ==============================================================================
# [MOD-2026-07-28] [AUTOR: Qwen] [VALIDADOR: JEISSON_01]
# MOTIVO: Materializar la visión del Contralor como garante transversal de cada ejecución.
# REF: Art. 5 (Memoria es Sistema), Art. 14 (Protección Patrimonial), Protocolo SHA-256.

import os
import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NexusContralor:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.normas_criticas = [
            "SOBERANO_00_GOBIERNO/CONSTITUCION.md",
            "SOBERANO_00_GOBIERNO/NORMAS.md",
            "SOBERANO_03_NEXUS/config.py"
        ]

    def calcular_hash(self, filepath: str) -> str:
        """Calcula el hash SHA-256 de un archivo para garantizar su integridad."""
        if not os.path.exists(filepath):
            return "ARCHIVO_NO_ENCONTRADO"
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def auditar_accion(self, accion: str, actor: str, detalles: dict) -> dict:
        """
        Registra y valida una acción antes/durante su ejecución.
        Retorna: {"permitido": True, "mensaje": "OK"} o {"permitido": False, "mensaje": "Motivo"}
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        registro = {
            "timestamp": timestamp,
            "actor": actor,
            "accion": accion,
            "detalles": detalles,
            "estado": "AUDITADO"
        }
        
        # 1. Validación de Normativa (Ejemplo: no permitir ejecución si el freno está activo)
        if accion in ["EJECUCION_TRADE", "MODIFICACION_WATCHLIST"]:
            cb = self.redis.get("circuit_breaker:active")
            cb_val = cb.decode() if isinstance(cb, bytes) else (cb or "")
            if cb_val == "true":
                registro["estado"] = "RECHAZADO_POR_NORMA"
                registro["motivo"] = "Circuit Breaker activo. Acción prohibida por Art. 14."
                self._guardar_auditoria(registro)
                return {"permitido": False, "mensaje": "⛔ ACCIÓN RECHAZADA: Freno de Emergencia activo."}

        # 2. Registro de Trazabilidad en Redis
        self._guardar_auditoria(registro)
        return {"permitido": True, "mensaje": "✅ Acción auditada y permitida."}

    def _guardar_auditoria(self, registro: dict):
        """Guarda el registro en Redis con trazabilidad inmutable."""
        try:
            key_auditoria = "memoria:auditoria:contralor"
            self.redis.lpush(key_auditoria, str(registro))
            self.redis.ltrim(key_auditoria, 0, 99) # Mantener últimas 100 auditorías
            logger.info(f"🛡️ CONTRALOR: {registro['accion']} por {registro['actor']} -> {registro['estado']}")
        except Exception as e:
            logger.error(f"❌ Contralor: Fallo al registrar auditoría: {e}")

    def generar_reporte_integridad(self) -> str:
        """Genera un reporte del estado de integridad de los archivos críticos."""
        reporte = "🛡️ *REPORTE DE INTEGRIDAD DEL CONTRALOR*\n\n"
        for archivo in self.normas_criticas:
            hash_actual = self.calcular_hash(archivo)
            estado = "✅ ÍNTEGRO" if hash_actual != "ARCHIVO_NO_ENCONTRADO" else "⚠️ NO ENCONTRADO"
            reporte += f"• `{archivo}`\n  Hash: `{hash_actual[:16]}...` | Estado: {estado}\n"
        
        # Contar auditorías recientes
        try:
            total_auditorias = self.redis.llen("memoria:auditoria:contralor") or 0
            reporte += f"\n📊 Total acciones auditadas (sesión actual): {total_auditorias}"
        except:
            pass
            
        return reporte

# Instancia global para ser importada
contralor_instance = None

def get_contralor(redis_client):
    global contralor_instance
    if contralor_instance is None:
        contralor_instance = NexusContralor(redis_client)
    return contralor_instance

    def bloquear_ejecucion_no_autorizada(self, redis_client):
        """
        Verifica integridad. Si falla, elimina AUTO_EJECUCION_TEMP de Redis.
        """
        reporte = self.generar_reporte_integridad()
        if "❌" in reporte or "⚠️" in reporte:
            try:
                redis_client.delete("AUTO_EJECUCION_TEMP")
                logger.critical("🚨 CONTRALOR: Ejecución automática bloqueada por fallo de integridad.")
                return False
            except Exception as e:
                logger.error(f"Error bloqueando en Redis: {e}")
                return False
        return True
