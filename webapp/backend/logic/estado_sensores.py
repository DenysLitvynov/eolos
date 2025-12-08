"""
Autor: Víctor Morant
Fecha: 20-11-2025
Descripción: Lógica de negocio para obtener el estado de los sensores (bicicletas).
"""

# ---------------------------------------------------------

from sqlalchemy.orm import Session
from sqlalchemy import func
from ..db.models import Bicicleta, PlacaSensores, Medida, Estacion
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------

class LogicaEstadoSensores:

    def calcular_tiempo_transcurrido(self, fecha_hora):
        """
        Calcula el tiempo transcurrido desde una fecha hasta ahora.
        Retorna una cadena legible como "5 min", "2 horas", etc.
        
        Args:
            fecha_hora (datetime): Fecha a comparar
        
        Returns:
            str: Tiempo transcurrido en formato legible
        """
        # Asegurarse de que ambas datetimes sean offset-aware o offset-naive
        ahora = datetime.now(timezone.utc)
        
        # Si fecha_hora es offset-naive, hacerla offset-aware
        if fecha_hora.tzinfo is None:
            fecha_hora = fecha_hora.replace(tzinfo=timezone.utc)
        
        diff = ahora - fecha_hora
        
        minutos = diff.total_seconds() // 60
        horas = minutos // 60
        dias = horas // 24
        
        if minutos < 1:
            return "Hace poco"
        elif minutos < 60:
            return f"{int(minutos)} min"
        elif horas < 24:
            return f"{int(horas)} hora{'s' if horas > 1 else ''}"
        else:
            return f"{int(dias)} día{'s' if dias > 1 else ''}"

    def obtener_todas_bicicletas(self, db: Session):
        """
        Obtiene todas las bicicletas con su información de sensores y estación.
        
        Args:
            db (Session): Sesión de BD.
        
        Returns:
            list: Lista de dicts con datos de bicicletas
        """
        try:
            bicicletas = db.query(Bicicleta).all()
            
            resultado = []
            for bici in bicicletas:
                # Obtener placa sensor
                placa = db.query(PlacaSensores).filter(
                    PlacaSensores.bicicleta_id == bici.bicicleta_id
                ).first()
                
                # Obtener estación
                estacion = db.query(Estacion).filter(
                    Estacion.estacion_id == bici.estacion_id
                ).first()
                
                # Calcular última actualización
                ultima_actualizacion = "Sin datos"
                if placa and placa.ult_actualizacion_estado:
                    ultima_actualizacion = self.calcular_tiempo_transcurrido(
                        placa.ult_actualizacion_estado
                    )
                
                resultado.append({
                    "id": bici.bicicleta_id,
                    "estado": placa.estado if placa else "Desconocido",
                    "ultimaActualizacion": ultima_actualizacion,
                    "parada": estacion.nombre if estacion else "Estación desconocida"
                })
            
            return resultado
        except Exception as e:
            raise RuntimeError(f"Error obteniendo bicicletas: {e}")

# ---------------------------------------------------------