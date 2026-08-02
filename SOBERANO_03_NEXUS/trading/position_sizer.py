import logging
from typing import Dict

logger = logging.getLogger(__name__)

class PositionSizer:
    def __init__(self, capital_total: float):
        self.capital_total = capital_total
        self.riesgo_maximo_pct = 0.01
        self.factor_seguridad_normal = 0.4
        self.factor_seguridad_reducido = 0.2
    
    def calcular_tamaño_posicion(self, precio_entrada: float, stop_loss: float, factor_ia: float = 1.0) -> Dict:
        resultado = {"acciones": 0, "inversion_total": 0.0, "riesgo_maximo": 0.0, "riesgo_pct": 0.0, "factor_riesgo_usado": 0.0, "razon": ""}
        try:
            if precio_entrada <= 0 or stop_loss <= 0 or precio_entrada <= stop_loss or self.capital_total <= 0:
                resultado["razon"] = "Datos inválidos para cálculo"
                return resultado
            
            riesgo_por_accion = precio_entrada - stop_loss
            factor_riesgo = self.factor_seguridad_normal if factor_ia >= 1.0 else self.factor_seguridad_reducido
            
            acciones = int((self.capital_total * self.riesgo_maximo_pct * factor_riesgo) / riesgo_por_accion)
            if acciones <= 0:
                resultado["razon"] = "Capital insuficiente para 1 acción"
                return resultado
            
            resultado["acciones"] = acciones
            resultado["inversion_total"] = round(acciones * precio_entrada, 2)
            resultado["riesgo_maximo"] = round(acciones * riesgo_por_accion, 2)
            resultado["riesgo_pct"] = round((resultado["riesgo_maximo"] / self.capital_total) * 100, 4)
            resultado["factor_riesgo_usado"] = factor_riesgo
            resultado["razon"] = f"Posición calculada: {acciones} acciones"
            return resultado
        except Exception as e:
            resultado["razon"] = f"Error: {str(e)[:50]}"
            return resultado
