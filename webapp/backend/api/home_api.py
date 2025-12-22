"""
Autor: JINWEI
Fecha: 21-12-2025
Descripción: Home API (landing registrado).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import Usuario
from ..logic.home_logic import LogicaHome
from .perfil_api import get_current_user  # ✅ reutiliza JWT

router = APIRouter()
logica = LogicaHome()


@router.get("/home")
def get_home(
    lat: float | None = Query(default=None),
    lon: float | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return logica.obtener_home(
        db,
        usuario_id=str(current_user.usuario_id),
        lat=lat,
        lon=lon,
    )
