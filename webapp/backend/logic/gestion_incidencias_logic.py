"""
Autor: Ariel Bejaran
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

    def listar_incidencias_por_fuente(self, db: Session, fuentes: list) -> List[Incidencia]:
        """Devuelve incidencias filtradas por fuentes específicas.

        Args:
            db: Sesión de base de datos.
            fuentes: Lista de enum FuenteReporte a filtrar (ej. [FuenteReporte.app, FuenteReporte.web]).

        Returns:
            Lista de incidencias que coinciden con las fuentes indicadas.
        """
        if not fuentes:
            return []
        return db.query(Incidencia).filter(Incidencia.fuente.in_(fuentes)).order_by(Incidencia.fecha_reporte.desc()).all()
