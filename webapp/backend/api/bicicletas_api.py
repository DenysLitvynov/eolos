"""
Autor: Hugo Belda Revert
Fecha: 21-12-2025
Descripción: Rutas API para estaciones de bicicletas.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..logic.bicicletas import LogicaBicicletas
from ..db.database import get_db

router = APIRouter(prefix="/bicicletas", tags=["bicicletas"])

@router.get("/estaciones")
def obtener_estaciones(db: Session = Depends(get_db)):
    logica = LogicaBicicletas()
    return logica.obtener_estaciones(db)
