"""
Autor: JINWEI
Fecha: 17-11-2025
Descripción: Lógica de negocio de la tabla 'incidencias'.
"""

from typing import List
from uuid import uuid4

from sqlalchemy.orm import Session

from ..db.models import (
    Incidencia,
    Bicicleta,
    Usuario,
    EstadoIncidencia,
    FuenteReporte,
)


class LogicaIncidencias:
    """
    Encapsula la lógica relacionada con la creación y consulta de incidencias.
    """

    # -------- Métodos internos (helpers) --------
    def _obtener_usuario(self, db: Session, usuario_id: str) -> Usuario:
        """
        Recupera un usuario por su ID.
        Lanza ValueError si no existe.
        """
        usuario = db.query(Usuario).filter(Usuario.usuario_id == str(usuario_id)).first()
        if not usuario:
            raise ValueError("Usuario no encontrado")
        return usuario

    def _obtener_bicicleta_por_short(self, db: Session, short_code: str) -> Bicicleta:
        """
        Busca una bicicleta usando su short_code (VLC001, VLC045, etc.).
        Lanza ValueError si no existe ninguna bicicleta con ese código.
        """
        short_code = str(short_code).strip()
        bici = db.query(Bicicleta).filter(Bicicleta.short_code == short_code).first()
       	if not bici:
            raise ValueError(f"Bicicleta no encontrada para el código: {short_code}")
        return bici

    # -------- API pública --------
    def crear_incidencia(
        self,
        db: Session,
        *,
        usuario_id: str,
        short_code: str,
        descripcion: str,
        fuente_str: str,
    ) -> Incidencia:
        """
        Crea una incidencia asociada a un usuario y a una bicicleta.

        Parámetros:
          - usuario_id: viene del JWT (el backend lo resuelve a partir del token)
          - short_code: código corto de la bici (VLC001, VLC045…)
          - descripcion: texto descriptivo del problema
          - fuente_str: "admin", "app" o "web", según desde dónde se reporta
        """

        # La descripción es obligatoria
        if not descripcion or not descripcion.strip():
            raise ValueError("La descripción no puede estar vacía")

        descripcion = descripcion.strip()

        # Normalizar y validar la fuente de reporte
        fuente_str = (fuente_str or "").strip().lower()
        if fuente_str not in {"app", "admin", "web"}:
            raise ValueError("Fuente no válida (debe ser 'app', 'admin' o 'web')")

        fuente_enum = FuenteReporte(fuente_str)

        # Verificar que el usuario y la bicicleta existan
        usuario = self._obtener_usuario(db, usuario_id)
        bici = self._obtener_bicicleta_por_short(db, short_code)

        # Crear instancia de Incidencia
        incidencia = Incidencia(
            incidencia_id=str(uuid4()),
            usuario_id=str(usuario.usuario_id),
            bicicleta_id=str(bici.bicicleta_id),
            descripcion=descripcion,
            estado=EstadoIncidencia.nuevo,
            fuente=fuente_enum,
            # fecha_reporte: la base de datos asigna NOW() por defecto
        )

        # Guardar en la base de datos
        db.add(incidencia)
        db.commit()
        db.refresh(incidencia)
        return incidencia

    def listar_incidencias_por_usuario(
        self,
        db: Session,
        *,
        usuario_id: str,
    ) -> List[Incidencia]:
        """
        Devuelve todas las incidencias que pertenecen a un usuario,
        ordenadas de la más reciente a la más antigua.
        """
        return (
            db.query(Incidencia)
            .filter(Incidencia.usuario_id == str(usuario_id))
            .order_by(Incidencia.fecha_reporte.desc())
            .all()
        )
