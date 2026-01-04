"""recompensas_logic.py
@Author: Ariel Bejaran
@Date: 2024-06-15
@Description: Lógica de negocio relacionada con las recompensas en la aplicación.
"""
from ..db.models import Recompensa as RecompensaDB
from ..db.models import RecompensaUsuario,RecompensaObtenida,Trayecto
from sqlalchemy.orm import Session
from typing import List
from ..pojos.recompensa import Recompensa as RecompensaPOJO
from sqlalchemy import func # Necesario para la función SUM() de SQL
from datetime import datetime,timezone


class RecompensasLogic:
    
    def obtener_recompensas(self, db: Session) -> List[RecompensaPOJO]:
        """Obtiene todas las recompensas disponibles en la base de datos.
        
        Args:
            db: Sesión de base de datos.

        Returns:
            Lista de objetos RecompensaPOJO (o dicts) listos para la API.
        """
        
        try:
            recompensas_db = db.query(RecompensaDB).all()
            
            
            recompensas = []
            for recompensa_db in recompensas_db:
                
                recompensa_dict = {
                    "recompensa_id": str(recompensa_db.recompensa_id), # uuid debe convertirse a string para JSON/Pydantic
                    "titulo": recompensa_db.titulo,
                    "descripcion": recompensa_db.descripcion,
                    "fecha_inicio": recompensa_db.fecha_inicio,
                    "fecha_fin": recompensa_db.fecha_fin,
                    "criterio_num_km": recompensa_db.criterio_num_km
                }
                recompensas.append(recompensa_dict) 
            
            return recompensas
        
        except Exception as e:
            raise RuntimeError(f"Error al obtener recompensas: {str(e)}")
    
    def obtener_codigo_recompensa(self, db: Session, recompensa_id: str) -> str:
        """Obtiene el código de una recompensa específica por su ID.

        Args:
            db: Sesión de base de datos.
            recompensa_id: ID de la recompensa.

        Returns:
            Código de la recompensa.

        Raises:
            ValueError: Si la recompensa no se encuentra.
        """
        recompensa = db.query(RecompensaDB).filter(RecompensaDB.recompensa_id == recompensa_id).first()
        if not recompensa:
            raise ValueError("Recompensa no encontrada")
        
        return recompensa.codigo
    
    
    # ---------------------------------------------------------
    
    def obtener_distancia_total_mes_actual(self, db: Session, userid: str) -> float:
        """
        Calcula la distancia total recorrida por un usuario en el mes actual 
        accediendo a la tabla Trayectos y sumando 'distancia_total'.
        
        Args:
            db: Sesión de base de datos.
            userid: ID del usuario.

        Returns:
            Distancia total recorrida en kilómetros en el mes actual.
        """
        try:
            ahora = datetime.now(timezone.utc)
            # Definimos el inicio del mes actual
            inicio_mes = datetime(ahora.year, ahora.month, 1, tzinfo=timezone.utc)
            
            # Definimos el inicio del siguiente mes para definir el final del rango
            if ahora.month == 12:
                fin_mes = datetime(ahora.year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                fin_mes = datetime(ahora.year, ahora.month + 1, 1, tzinfo=timezone.utc)
                
            # Usamos func.sum para sumar la columna distancia_total
            distancia_total = db.query(func.sum(Trayecto.distancia_total)).filter(
                Trayecto.usuario_id == userid,
                Trayecto.fecha_inicio >= inicio_mes,
                Trayecto.fecha_inicio < fin_mes,
                Trayecto.distancia_total.isnot(None) # Aseguramos que solo sume trayectos con distancia
            ).scalar()
            
            return distancia_total if distancia_total is not None else 0.0 
        except Exception as e:
            raise RuntimeError(f"Error al calcular distancia total del mes: {str(e)}")
    
    # ---------------------------------------------------------
    
    def actualizar_km_acumulados_este_mes(self, db: Session, usuario_id: str) -> float:
        """
        Obtiene la distancia recorrida por el usuario en el MES ACTUAL 
        y actualiza el campo km_acumulados en la tabla recompensas_usuario con ese valor.

        Args:
            db: Sesión de base de datos.
            usuario_id: ID del usuario.
            
        Returns:
            El valor de kilómetros actualizado (del mes actual).
        """
        try:
            # 1. Obtener la distancia total del mes actual
            km_mensuales = self.obtener_distancia_total_mes_actual(db, usuario_id)
            
            # 2. Buscar/Crear el registro en recompensas_usuario
            recompensa_stats = db.query(RecompensaUsuario).filter(
                RecompensaUsuario.usuario_id == usuario_id
            ).first()
            
            if recompensa_stats:
                # Si existe, actualizamos con el valor del mes actual
                recompensa_stats.km_acumulados = km_mensuales
            else:
                # Si no existe, creamos el registro
                recompensa_stats = RecompensaUsuario(
                    usuario_id=usuario_id,
                    km_acumulados=km_mensuales
                )
                db.add(recompensa_stats)
                
            # 3. Guardar el cambio
            db.commit()
            
            return km_mensuales
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error al actualizar km acumulados: {str(e)}")
    