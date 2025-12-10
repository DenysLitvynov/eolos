"""
Autor: Denys Litvynov Lymanets
Fecha: 05-12-2025
Descripción: Lógica de negocio específica para el panel de administración de mapas.
Permite obtener históricos completos sin restricciones de "solo hoy".
"""

# ---------------------------------------------------------

from datetime import datetime
from sqlalchemy.orm import Session
from typing import Dict
from ..pojos.posicion_gps import PosicionGPS
from .mapas import LogicaMapas

# ---------------------------------------------------------

class LogicaAdminMapas:
    
    def __init__(self):
        # Composición: Usamos la lógica base para cálculos de gases y querys
        self.logica_base = LogicaMapas()

    # ---------------------------------------------------------

    def obtener_mapa_admin(self, db: Session, tipo: str, fecha: datetime, lat_min: float, lon_min: float, lat_max: float, lon_max: float) -> Dict:
        """
        Obtiene los datos del mapa para un rango geográfico y una fecha histórica específica.
        
        Args:
            db (Session): Sesión de base de datos.
            tipo (str): Tipo de medida ('general', 'pm2_5', etc).
            fecha (datetime): Fecha del histórico.
            lat_min (float): Latitud mínima.
            lon_min (float): Longitud mínima.
            lat_max (float): Latitud máxima.
            lon_max (float): Longitud máxima.
            
        Returns:
            Dict: Diccionario con timestamps y datos por hora.
        """
        inf_izq = PosicionGPS(lat_min, lon_min)
        sup_der = PosicionGPS(lat_max, lon_max)

        # Normalización del tipo de string a lo que espera la lógica base
        # Nota: LogicaMapas espera "pm2_5" si viene del enum, o strings si se refactorizó.
        # Asumimos que la lógica base maneja la conversión de string a Enum internamente 
        # o pasamos el string normalizado.
        
        return self.logica_base.obtener_mapa_de_tipo_de_dia_de_destino(
            db, tipo, fecha, inf_izq, sup_der
        )
# ---------------------------------------------------------
