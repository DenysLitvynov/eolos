"""
Autor: Denys Litvynov Lymanets
Fecha: 19-11-2025
Descripción: Clase para representar una medida.
"""

from datetime import datetime
from .posicion_gps import PosicionGPS
from ..db.models import TipoMedidaEnum

# ---------------------------------------------------------

class Medida:
    def __init__(self, trayecto_id: str, placa_id: str, tipo: TipoMedidaEnum, valor: float, fecha_hora: datetime, posicion: PosicionGPS):
        """
        Inicializa una medida.

        Args:
            trayecto_id (str): ID del trayecto.
            placa_id (str): ID de la placa.
            tipo (TipoMedidaEnum): Tipo de medida.
            valor (float): Valor de la medida.
            fecha_hora (datetime): Fecha y hora.
            posicion (PosicionGPS): Posición GPS.
        """
        self.trayecto_id = trayecto_id
        self.placa_id = placa_id
        self.tipo = tipo
        self.valor = valor
        self.fecha_hora = fecha_hora
        self.posicion = posicion

# ---------------------------------------------------------

    def obtener_medida(self) -> dict:
        """
        Devuelve la medida como un diccionario.

        Returns:
            dict: Representación de la medida.
        """
        return {
            "trayecto_id": self.trayecto_id,
            "placa_id": self.placa_id,
            "tipo": self.tipo,
            "valor": self.valor,
            "fecha_hora": self.fecha_hora,
            "lat": self.posicion.lat,
            "lon": self.posicion.lon
        }

# ---------------------------------------------------------
