"""
Autor: GitHub Copilot (adaptado)
Fecha: 05-12-2025
Descripción: API auxiliares para la gestión de incidencias (lista simplificada para frontend).
Se reutiliza `LogicaIncidencias` y `get_current_user` para devolver una lista de incidencias
en un formato amigable para el frontend de `gestion_incidencias`.
"""

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import Incidencia, EstadoIncidencia
from ..logic.incidencias_logic import LogicaIncidencias
from ..logic.gestion_incidencias_logic import GestionIncidenciasLogic
from .perfil_api import get_current_user

router = APIRouter(prefix="/gestion-incidencias")
logica = LogicaIncidencias()
gestion_logic = GestionIncidenciasLogic()


class IncidenciaListadoOut(BaseModel):
    titulo: str
    tiempo: str
    fuente: str
    esResuelto: bool


def _formatear_tiempo_relativo(fecha_reporte: datetime) -> str:
    """Devuelve una cadena simple tipo '5min', '1h 30min' o fecha.
    Se usa para mostrar en las tarjetas del frontend.
    """
    try:
        ahora = datetime.now(timezone.utc)
        # Asegurar ambos con tzinfo para poder restar
        if fecha_reporte.tzinfo is None:
            fecha_reporte = fecha_reporte.replace(tzinfo=timezone.utc)
        delta = ahora - fecha_reporte
        segundos = int(delta.total_seconds())
    except Exception:
        return "hace un momento"

    if segundos < 60:
        return "Hace: justo ahora"
    minutos = segundos // 60
    if minutos < 60:
        return f"Hace: {minutos}min"
    horas = minutos // 60
    minutos_rest = minutos % 60
    if horas < 24:
        if minutos_rest == 0:
            return f"Hace: {horas}h"
        return f"Hace: {horas}h {minutos_rest}min"
    # Más de un día: devolver fecha en formato ISO corto
    return fecha_reporte.strftime("%Y-%m-%d")


@router.get("/mias", response_model=List[IncidenciaListadoOut])
def listar_mis_incidencias(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> List[IncidenciaListadoOut]:
    """Devuelve una versión simplificada de las incidencias del usuario.

    Ruta montada como: GET /api/v1/gestion-incidencias/mias
    """
    try:
        incidencias = logica.listar_incidencias_por_usuario(db, usuario_id=str(current_user.usuario_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    resultado = []
    for inc in incidencias:
        titulo = inc.descripcion if getattr(inc, "descripcion", None) else "Incidencia"
        tiempo = _formatear_tiempo_relativo(inc.fecha_reporte) if getattr(inc, "fecha_reporte", None) else "Hace: ahora"
        fuente = getattr(inc.fuente, 'value', str(inc.fuente)) if inc.fuente is not None else "app"
        es_resuelto = (inc.estado == EstadoIncidencia.resuelto)

        resultado.append(
            IncidenciaListadoOut(
                titulo=titulo,
                tiempo=tiempo,
                fuente=fuente.title(),
                esResuelto=es_resuelto,
            )
        )

    return resultado


@router.get("/public", response_model=List[IncidenciaListadoOut])
def listar_incidencias_publicas(
    db: Session = Depends(get_db),
) -> List[IncidenciaListadoOut]:
    """Endpoint público de solo-lectura para pruebas en frontend.

    Ruta: GET /api/v1/gestion-incidencias/public
    Devuelve todas las incidencias sin requerir autenticación (solo para dev).
    """
    try:
        incidencias = gestion_logic.listar_todas_incidencias(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    resultado = []
    for inc in incidencias:
        titulo = inc.descripcion if getattr(inc, "descripcion", None) else "Incidencia"
        tiempo = _formatear_tiempo_relativo(inc.fecha_reporte) if getattr(inc, "fecha_reporte", None) else "Hace: ahora"
        fuente = getattr(inc.fuente, 'value', str(inc.fuente)) if inc.fuente is not None else "app"
        es_resuelto = (inc.estado.name == 'resuelto') if hasattr(inc.estado, 'name') else (inc.estado == 'resuelto')

        resultado.append(
            IncidenciaListadoOut(
                titulo=titulo,
                tiempo=tiempo,
                fuente=fuente.title(),
                esResuelto=es_resuelto,
            )
        )

    return resultado
