"""
Autor: Denys Litvynov Lymanets
Fecha: 19-11-2025
Descripción: Clase para representar una posición GPS.
"""

from math import radians, sin, cos, sqrt, atan2

# ---------------------------------------------------------

class PosicionGPS:
    def __init__(self, lat: float, lon: float):
        """
        Inicializa una posición GPS.

        Args:
            lat (float): Latitud.
            lon (float): Longitud.
        """
        self.lat = lat
        self.lon = lon

    # ---------------------------------------------------------

    def obtener_posicion_gps(self) -> 'PosicionGPS':
        """
        Devuelve la posición GPS actual.

        Returns:
            PosicionGPS: La instancia actual.
        """
        return self

    # ---------------------------------------------------------

    @staticmethod
    def distancia_entre_dos(pos1: 'PosicionGPS', pos2: 'PosicionGPS') -> float:
        """
        Calcula la distancia en metros entre dos posiciones GPS usando la fórmula de Haversine.

        Args:
            pos1 (PosicionGPS): Primera posición.
            pos2 (PosicionGPS): Segunda posición.

        Returns:
            float: Distancia en metros.
        """
        R = 6371.0  # Radio de la Tierra en km
        lat1, lon1 = radians(pos1.lat), radians(pos1.lon)
        lat2, lon2 = radians(pos2.lat), radians(pos2.lon)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c * 1000  # Convertir a metros
        return distance


# ---------------------------------------------------------
