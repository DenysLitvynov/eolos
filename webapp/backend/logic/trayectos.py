"""
Autor: Denys Litvynov Lymanets
Fecha: 19-11-2025
Descripción: Lógica de negocio para los trayectos.
"""

from sqlalchemy.orm import Session
from typing import Optional, Tuple
from datetime import datetime
import uuid
from ..db.models import Trayecto as DBTrayecto, Usuario, PlacaSensores, Medida as DBMedida, Bicicleta, Estacion, EstadoBicicleta
from ..pojos.posicion_gps import PosicionGPS
from ..pojos.medida import Medida as DTOMedida
from ..pojos.trayecto import Trayecto as DTOTrayecto  # Import agregado para usar la clase Trayecto


class LogicaTrayectos:

    # ---------------------------------------------------------

    def __init__(self):
        """
        Inicializa la lógica de trayectos.
        """
        pass

    # ---------------------------------------------------------

    def guardar_medida(self, db: Session, medida: DTOMedida) -> str:
        """
        Guarda una medida en la base de datos, generando el lectura_id.

        Args:
            db (Session): Sesión de BD.
            medida (DTOMedida): Objeto medida.

        Returns:
            str: "OK" si éxito.
        """
        try:
            lectura_id = str(uuid.uuid4())

            db_medida = DBMedida(
                lectura_id=lectura_id,
                placa_id=medida.placa_id,
                trayecto_id=medida.trayecto_id,
                fecha_hora=medida.fecha_hora,
                tipo=medida.tipo,
                valor=medida.valor,
                lat=medida.posicion.lat,
                lon=medida.posicion.lon
            )

            db.add(db_medida)

            db.commit()

            return "OK"
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error guardando medida: {e}")

    # ---------------------------------------------------------

    def iniciar_trayecto(self, db: Session, targeta_id: str, bicicleta_id: str, fecha_inicio: datetime, origen: PosicionGPS) -> str:
        """
        Inicia un nuevo trayecto.

        Args:
            db (Session): Sesión de BD.
            targeta_id (str): ID de la tarjeta.
            bicicleta_id (str): ID de la bicicleta.
            fecha_inicio (datetime): Fecha de inicio.
            origen (PosicionGPS): Posición de origen.

        Returns:
            str: trayecto_id generado.
        """
        try:
            origen_id = self.comprobar_estacion_bici(db, origen)
            if origen_id is None:
                raise ValueError("Origen no coincide con ninguna estación")

            usuario = db.query(Usuario).filter(Usuario.targeta_id == targeta_id).first()
            if not usuario:
                raise ValueError("Usuario no encontrado")

            trayecto_id = str(uuid.uuid4())
            trayecto = DBTrayecto(
                trayecto_id=trayecto_id,
                usuario_id=usuario.usuario_id,
                bicicleta_id=bicicleta_id,
                fecha_inicio=fecha_inicio,
                origen_estacion_id=origen_id
            )

            db.add(trayecto)
            db.commit()

            return trayecto_id
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error iniciando trayecto: {e}")

    # ---------------------------------------------------------

    def obtener_datos_trayecto(self, db: Session, trayecto_id: str) -> Tuple[str, str]:
        """
        Obtiene usuario_id y placa_id para un trayecto.

        Args:
            db (Session): Sesión de BD.
            trayecto_id (str): ID del trayecto.

        Returns:
            Tuple[str, str]: (usuario_id, placa_id)
        """
        try:
            trayecto = db.query(DBTrayecto).filter(DBTrayecto.trayecto_id == trayecto_id).first()
            if not trayecto:
                raise ValueError("Trayecto no encontrado")

            placa = db.query(PlacaSensores).filter(PlacaSensores.bicicleta_id == trayecto.bicicleta_id).first()
            if not placa:
                raise ValueError("Placa no encontrada")

            return trayecto.usuario_id, placa.placa_id
        except Exception as e:
            raise RuntimeError(f"Error obteniendo datos de trayecto: {e}")

    # ---------------------------------------------------------

    def finalizar_trayecto(self, db: Session, trayecto_id: str, fecha_fin: datetime, destino: PosicionGPS) -> str:
        """
        Finaliza un trayecto, calculando la distancia total internamente.

        Args:
            db (Session): Sesión de BD.
            trayecto_id (str): ID del trayecto.
            fecha_fin (datetime): Fecha de fin.
            destino (PosicionGPS): Posición de destino.

        Returns:
            str: "OK" si éxito.
        """
        try:
            destino_id = self.comprobar_estacion_bici(db, destino)
            if destino_id is None:
                raise ValueError("Destino no coincide con ninguna estación")

            trayecto = db.query(DBTrayecto).filter(DBTrayecto.trayecto_id == trayecto_id).first()
            if not trayecto:
                raise ValueError("Trayecto no encontrado")

            # Calcular distancia total usando la clase Trayecto
            trayecto_dto = DTOTrayecto(trayecto_id)
            distancia_total = trayecto_dto.calcular_distancia(db)

            trayecto.fecha_fin = fecha_fin
            trayecto.destino_estacion_id = destino_id
            trayecto.distancia_total = distancia_total

            db.commit()
            return "OK"
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error finalizando trayecto: {e}")

    # ---------------------------------------------------------

    def actualizar_estado_placa(self, db: Session, placa_id: str, estado: str, ult_actualizacion_estado: datetime) -> str:
        """
        Actualiza el estado de una placa.

        Args:
            db (Session): Sesión de BD.
            placa_id (str): ID de la placa.
            estado (str): Nuevo estado.
            ult_actualizacion_estado (datetime): Última actualización.

        Returns:
            str: "OK" si éxito.
        """
        try:
            placa = db.query(PlacaSensores).filter(PlacaSensores.placa_id == placa_id).first()
            if not placa:
                raise ValueError("Placa no encontrada")

            placa.estado = estado
            placa.ult_actualizacion_estado = ult_actualizacion_estado

            db.commit()
            return "OK"
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error actualizando placa: {e}")

    # ---------------------------------------------------------

    def actualizar_estado_bici(self, db: Session, bicicleta_id: str, posicion: PosicionGPS, estado: EstadoBicicleta) -> str:
        """
        Actualiza el estado de una bicicleta.

        Args:
            db (Session): Sesión de BD.
            bicicleta_id (str): ID de la bicicleta.
            posicion (PosicionGPS): Posición actual.
            estado (EstadoBicicleta): Nuevo estado.

        Returns:
            str: "OK" si éxito.
        """
        try:
            estacion_id = self.comprobar_estacion_bici(db, posicion)
            bici = db.query(Bicicleta).filter(Bicicleta.bicicleta_id == bicicleta_id).first()
            if not bici:
                raise ValueError("Bicicleta no encontrada")

            bici.estacion_id = estacion_id
            bici.estado = estado

            db.commit()
            return "OK"
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error actualizando bicicleta: {e}")

    # ---------------------------------------------------------

    def comprobar_estacion_bici(self, db: Session, posicion: PosicionGPS) -> Optional[int]:
        """
        Comprueba si la posición coincide con una estación.

        Args:
            db (Session): Sesión de BD.
            posicion (PosicionGPS): Posición a comprobar.

        Returns:
            Optional[int]: estacion_id si coincide, None si no.
        """
        try:
            estaciones = db.query(Estacion).all()
            threshold = 50.0  # metros
            min_dist = float('inf')
            closest_id = None

            for est in estaciones:
                est_pos = PosicionGPS(est.lat, est.lon)
                dist = PosicionGPS.distancia_entre_dos(posicion, est_pos)
                if dist < min_dist:
                    min_dist = dist
                    closest_id = est.estacion_id

            if min_dist <= threshold:
                return closest_id
            return None
        except Exception as e:
            raise RuntimeError(f"Error comprobando estación: {e}")

    # ---------------------------------------------------------

