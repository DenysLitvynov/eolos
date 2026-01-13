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
from datetime import datetime
import uuid


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
            
            # Gracias a 'from_attributes=True' en el POJO, podemos hacer esto:
            return [RecompensaPOJO.model_validate(r) for r in recompensas_db]
            
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
    
    
    def procesar_y_obtener_recompensas(self, db: Session, usuario_id: str):
        try:
            # 1. Obtener KM del usuario en el mes actual
            km_usuario = self.obtener_distancia_total_mes_actual(db, usuario_id)

            # 2. Obtener IDs de recompensas que el usuario YA TIENE
            obtenidas_db = db.query(RecompensaObtenida.recompensa_id).filter(
                RecompensaObtenida.usuario_id == usuario_id
            ).all()
            ids_ya_obtenidos = [r[0] for r in obtenidas_db]

            # 3. Buscar recompensas que HA ALCANZADO pero NO TIENE guardadas
            recompensas_nuevas = db.query(RecompensaDB).filter(
                RecompensaDB.criterio_num_km <= km_usuario,
                ~RecompensaDB.recompensa_id.in_(ids_ya_obtenidos)
            ).all()

            # 4. GUARDADO AUTOMÁTICO: Insertar en recompensas_obtenidas
            for r_db in recompensas_nuevas:
                nueva_relacion = RecompensaObtenida(
                    id=str(uuid.uuid4()),
                    usuario_id=usuario_id,
                    recompensa_id=r_db.recompensa_id,
                    # SOLUCIÓN AL ERROR 500: Generamos el código único obligatorio
                    codigo_unico=f"REW-{usuario_id[:4]}-{r_db.recompensa_id[:4]}-{uuid.uuid4().hex[:4]}".upper()
                )
                db.add(nueva_relacion)
            
            if recompensas_nuevas:
                db.commit() # Guardamos cambios en la base de datos

            # 5. CONSTRUIR RESPUESTA PARA EL FRONTEND
            todas_las_recompensas = db.query(RecompensaDB).all()
            
            # Volvemos a consultar los IDs obtenidos (incluyendo los nuevos)
            ids_finales = [r[0] for r in db.query(RecompensaObtenida.recompensa_id).filter(
                RecompensaObtenida.usuario_id == usuario_id
            ).all()]

            resultado = {
                "obtenidas": [],
                "proximas": []
            }

            for r in todas_las_recompensas:
                # Estructura limpia para el JS icon_selector
                item = {
                    "recompensa_id": r.recompensa_id,
                    "titulo": r.titulo,
                    "descripcion": r.descripcion,
                    "criterio_num_km": r.criterio_num_km,
                    "alcanzada": r.recompensa_id in ids_finales
                }
                
                if item["alcanzada"]:
                    resultado["obtenidas"].append(item)
                else:
                    resultado["proximas"].append(item)

            return resultado

        except Exception as e:
            db.rollback()
            print(f"DEBUG LOGIC ERROR: {str(e)}") # Esto te dirá el error exacto en consola
            raise RuntimeError(f"Error procesando recompensas: {str(e)}")
        
    # ---------------------------------------------------------
    
    def obtener_distancia_total_mes_actual(self, db: Session, userid: str) -> float:
        try:
            # Quitamos timezone.utc para evitar conflictos de tipos con la DB
            ahora = datetime.now() 
            inicio_mes = datetime(ahora.year, ahora.month, 1)
            
            if ahora.month == 12:
                fin_mes = datetime(ahora.year + 1, 1, 1)
            else:
                fin_mes = datetime(ahora.year, ahora.month + 1, 1)
                
            # Ejecutamos la suma
            distancia_total = db.query(func.sum(Trayecto.distancia_total)).filter(
                Trayecto.usuario_id == userid,
                Trayecto.fecha_inicio >= inicio_mes,
                Trayecto.fecha_inicio < fin_mes
            ).scalar()
            
            return float(distancia_total) if distancia_total is not None else 0.0 
        except Exception as e:
            print(f"Error SQL: {e}") # Esto saldrá en tu terminal de Python
            raise RuntimeError(f"Error al calcular distancia: {str(e)}")
        
    # ---------------------------------------------------------
    
    def obtener_estado_recompensas_usuario(self, db: Session, usuario_id: str):
        """
        Obtiene el estado de todas las recompensas para un usuario específico,
        indicando si ha alcanzado cada una según sus kilómetros acumulados.
        Args:
            db: Sesión de base de datos.
            usuario_id: ID del usuario.
        Returns:
            Lista de diccionarios con el estado de cada recompensa.
        """
        
        try:
            # 1. Obtenemos los KM actuales del usuario (puedes usar el mes actual o total)
            km_usuario = self.obtener_distancia_total_mes_actual(db, usuario_id)
            
            # 2. Obtenemos todas las recompensas configuradas
            recompensas_db = db.query(RecompensaDB).all()
            
            # 3. Construimos la lista con el estado de "alcanzada"
            resultado = []
            for r in recompensas_db:
                # Marcamos como True si los KM del usuario superan el criterio
                estado = {
                    "recompensa_id": r.recompensa_id,
                    "titulo": r.titulo,
                    "descripcion": r.descripcion,
                    "criterio_num_km": r.criterio_num_km,
                    "km_actuales": km_usuario,
                    "alcanzada": km_usuario >= r.criterio_num_km
                }
                resultado.append(estado)
                
            return resultado
        except Exception as e:
            raise RuntimeError(f"Error al procesar estado de recompensas: {str(e)}")
    
    def actualizar_km_acumulados_este_mes(self, db: Session, usuario_id: str) -> float:
        """
        Obtiene la distancia recorrida por el usuario en el MES ACTUAL self.obtener_di
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
    