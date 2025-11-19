"""
Autor: Denys Litvynov Lymanets
Fecha: 19-11-2025
Descripción: Clase para representar un trayecto.
"""

from sqlalchemy.orm import Session
from typing import List
from ..db.models import Medida
from .posicion_gps import PosicionGPS

# ---------------------------------------------------------

class Trayecto:
    def __init__(self, trayecto_id: str):
        """
        Inicializa un trayecto con su ID.

        Args:
            trayecto_id (str): ID del trayecto.
        """
        self.trayecto_id = trayecto_id

# ---------------------------------------------------------

    def obtener_trayecto(self, db: Session) -> List[PosicionGPS]:
        """
        Obtiene la lista de posiciones GPS del trayecto desde la base de datos.

        Args:
            db (Session): Sesión de la base de datos.

        Returns:
            List[PosicionGPS]: Lista de posiciones.
        """
        medidas = db.query(Medida).filter(Medida.trayecto_id == self.trayecto_id).order_by(Medida.fecha_hora).all()
        return [PosicionGPS(m.lat, m.lon) for m in medidas]

# ---------------------------------------------------------

    def calcular_distancia(self, db: Session) -> float:
        """
        Calcula la distancia total del trayecto en metros.

        Args:
            db (Session): Sesión de la base de datos.

        Returns:
            float: Distancia total en metros.
        """
        posiciones = self.obtener_trayecto(db)
        if len(posiciones) < 2:
            return 0.0
        total = 0.0
        for i in range(1, len(posiciones)):
            total += PosicionGPS.distancia_entre_dos(posiciones[i-1], posiciones[i])
        return total
    
# ---------------------------------------------------------
