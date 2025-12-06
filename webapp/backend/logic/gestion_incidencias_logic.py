"""
Autor: GitHub Copilot (adaptado)
Fecha: 06-12-2025
Descripción: Lógica específica para la página de gestión de incidencias.
Contiene funciones auxiliares para listar incidencias públicas (uso en frontend de pruebas).
"""

from typing import List
from sqlalchemy.orm import Session

from ..db.models import Incidencia


class GestionIncidenciasLogic:
    """Lógica para la página de gestión de incidencias.

    NOTA: Estas funciones se usan por el endpoint público de pruebas y no
    reemplazan la lógica de negocio de `incidencias_logic.py`.
    """

    def listar_todas_incidencias(self, db: Session) -> List[Incidencia]:
        """Devuelve todas las filas de la tabla `incidencias`, ordenadas por fecha (desc).

        Usar solo en entornos de desarrollo o para endpoints de depuración.
        """
        return db.query(Incidencia).order_by(Incidencia.fecha_reporte.desc()).all()
