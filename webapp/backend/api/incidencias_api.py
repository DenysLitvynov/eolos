"""
Autor: JINWEI
Fecha: 17-11-2025
Descripción: API de incidencias (crear + listar) utilizando autenticación JWT Bearer.
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import Usuario, Incidencia
from ..logic.incidencias_logic import LogicaIncidencias
from .perfil_api import get_current_user  # Reutiliza el método existente para obtener el usuario desde el JWT

router = APIRouter()
logica = LogicaIncidencias()


# ====== Modelos Pydantic ======

class IncidenciaCreateIn(BaseModel):
    """
    Modelo de entrada para la creación de una incidencia.
    El cliente debe enviar:
      - bicicleta_id: Código de la bicicleta (ej. "VLC001")
      - descripcion: Texto descriptivo de la incidencia
      - fuente: Origen de la incidencia ("admin" o "app")
    """
    bicicleta_id: str = Field(..., max_length=20)
    descripcion: str = Field(..., min_length=1)
    fuente: str = Field(..., max_length=10)  # "admin" / "app"


class IncidenciaOut(BaseModel):
    """
    Modelo de salida que se devuelve al cliente.
    Incluye información completa de la incidencia registrada.
    """
    incidencia_id: str
    usuario_id: str
    bicicleta_id: str
    descripcion: str
    fecha_reporte: datetime
    estado: str
    fuente: str

    class Config:
        from_attributes = True


# ====== Rutas de la API ======

@router.post("/incidencias", response_model=IncidenciaOut, status_code=201)
def crear_incidencia(
    data: IncidenciaCreateIn,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> IncidenciaOut:
    """
    Crea una nueva incidencia asociada al usuario autenticado.
    - Valida el bicicleta_id y los datos de entrada.
    - Usa la lógica de negocio para registrar la incidencia.
    - Devuelve la incidencia recién creada.

    Si ocurre un error controlado (ej.: bici no encontrada),
    se devuelve un error 400 con el mensaje correspondiente.
    """
    try:
        incidencia = logica.crear_incidencia(
            db,
            usuario_id=str(current_user.usuario_id),
            bicicleta_id=data.bicicleta_id,
            descripcion=data.descripcion,
            fuente_str=data.fuente,
        )
    except ValueError as e:
        # Error de lógica: datos inválidos o bicicleta inexistente
        raise HTTPException(status_code=400, detail=str(e))

    return IncidenciaOut.model_validate(incidencia)


@router.get("/incidencias/mias", response_model=List[IncidenciaOut])
def listar_mis_incidencias(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[IncidenciaOut]:
    """
    Devuelve todas las incidencias creadas por el usuario autenticado.
    - No incluye incidencias de otros usuarios.
    - Devuelve la lista en formato seguro y serializable.

    Retorna una lista vacía si el usuario no tiene incidencias registradas.
    """
    incidencias = logica.listar_incidencias_por_usuario(
        db,
        usuario_id=str(current_user.usuario_id),
    )
    return [IncidenciaOut.model_validate(i) for i in incidencias]
