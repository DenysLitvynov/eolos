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
                    "placa_id": str(placa.placa_id) if placa else None,
                    "estado": placa.estado if placa else "Desconocido",
                    "ultimaActualizacion": ultima_actualizacion,
                    "parada": estacion.nombre if estacion else "Estación desconocida"
                })
            
            return resultado
        except Exception as e:
            raise RuntimeError(f"Error obteniendo bicicletas: {e}")

    def obtener_mediciones_placa(self, db: Session, placa_id: str, fecha_inicio: str = None, fecha_fin: str = None):
        """
        Obtiene todas las mediciones de una placa con rango de fechas opcional.
        
        Args:
            db (Session): Sesión de BD.
            placa_id (str): ID de la placa.
            fecha_inicio (str): Fecha inicio en formato ISO (opcional)
            fecha_fin (str): Fecha fin en formato ISO (opcional)
        
        Returns:
            list: Lista de mediciones ordenadas por fecha
        """
        try:
            query = db.query(Medida).filter(Medida.placa_id == placa_id)
            
            # Filtrar por rango de fechas si se proporcionan
            if fecha_inicio:
                fecha_inicio_dt = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
                query = query.filter(Medida.fecha_hora >= fecha_inicio_dt)
            
            if fecha_fin:
                fecha_fin_dt = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
                query = query.filter(Medida.fecha_hora <= fecha_fin_dt)
            
            mediciones = query.order_by(Medida.fecha_hora.asc()).all()
            
            if not mediciones:
                raise ValueError(f"No hay mediciones para la placa {placa_id}")
            
            return [
                {
                    "lectura_id": str(m.lectura_id),
                    "valor": float(m.valor),
                    "fecha_hora": m.fecha_hora.isoformat(),
                    "tipo": m.tipo,
                    "lat": float(m.lat) if m.lat else None,
                    "lon": float(m.lon) if m.lon else None,
                    "es_anomalo": m.valor < 0 or m.valor > 200
                }
                for m in mediciones
            ]
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error obteniendo mediciones: {e}")

    def eliminar_medicion(self, db: Session, lectura_id: str):
        """
        Elimina una medición específica por su lectura_id.
        
        Args:
            db (Session): Sesión de BD.
            lectura_id (str): ID de la lectura/medición.
        
        Returns:
            dict: Mensaje de confirmación
        """
        try:
            medicion = db.query(Medida).filter(Medida.lectura_id == lectura_id).first()
            
            if not medicion:
                raise ValueError(f"Medición con ID {lectura_id} no encontrada")
            
            db.delete(medicion)
            db.commit()
            
            return {"mensaje": "Medición eliminada correctamente"}
        except ValueError:
            raise
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error eliminando medición: {e}")

    def eliminar_mediciones_anomalas(self, db: Session, placa_id: str):
        """
        Elimina todas las mediciones anómalas (< 0 o > 200) de una placa.
        
        Args:
            db (Session): Sesión de BD.
            placa_id (str): ID de la placa.
        
        Returns:
            dict: Información sobre mediciones eliminadas
        """
        try:
            mediciones = db.query(Medida).filter(
                Medida.placa_id == placa_id,
                (Medida.valor < 0) | (Medida.valor > 200)
            ).all()
            
            cantidad = len(mediciones)
            
            for medicion in mediciones:
                db.delete(medicion)
            
            db.commit()
            
            return {
                "mensaje": f"{cantidad} medición(es) anómala(s) eliminada(s)",
                "cantidad": cantidad
            }
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error eliminando mediciones anómalas: {e}")

# ---------------------------------------------------------