"""
Autor: Denys Litvynov Lymanets
Fecha: 21-12-2025
Descripción: Lógica de negocio para obtener estaciones de bicicletas (Valenbisi).
"""


from typing import List, Dict
from sqlalchemy.orm import Session
from ..db.models import Estacion, Bicicleta, EstadoBicicleta

class LogicaBicicletas:

    def __init__(self):
        pass

    def obtener_estaciones(self, db: Session) -> List[Dict]:
        """
        Obtiene la lista de estaciones de bicicletas desde la base de datos.

        Args:
            db (Session): Sesión de base de datos.

        Returns:
            List[Dict]: Lista de estaciones con su información.
        """
        try:
            estaciones_db = db.query(Estacion).all()
            
            resultado = []
            for estacion in estaciones_db:
                # Contar bicicletas disponibles (estacionadas)
                # Asumimos que la relación 'bicicletas' está disponible
                bicis_disponibles = sum(1 for b in estacion.bicicletas if b.estado == EstadoBicicleta.estacionada)
                
                capacidad = estacion.capacidad
                huecos_libres = capacidad - bicis_disponibles
                if huecos_libres < 0:
                    huecos_libres = 0

                estacion_dict = {
                    "name": estacion.nombre,
                    "available_bikes": bicis_disponibles,
                    "available_stands": huecos_libres,
                    "total_stands": capacidad,
                    "lat": estacion.lat,
                    "lon": estacion.lon,
                    "updated_at": None # No tenemos fecha de actualización en la tabla Estacion
                }
                resultado.append(estacion_dict)
            
            return resultado

        except Exception as e:
            print(f"Error obteniendo estaciones de bicicletas de la BD: {e}")
            return []
