"""
Autor: JINWEI
Fecha: 28-12-2025
Descripción: API para contaminación en tiempo real por estación usando el punto más cercano en calidad_general.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from ..db.database import get_db
from ..logic.contaminacion_logic import LogicaContaminacion

router = APIRouter()
logica = LogicaContaminacion()


class Punto(BaseModel):
    lat: Optional[float] = None
    lon: Optional[float] = None


class MedicionOut(BaseModel):
    valor: Optional[float] = None
    color: Optional[str] = None
    fecha_hora: Optional[str] = None
    punto: Punto


class EstacionContaminacionOut(BaseModel):
    estacion_id: int
    nombre: Optional[str] = None
    estacion: Punto
    medicion: MedicionOut


class ContaminacionResponse(BaseModel):
    count: int
    items: List[EstacionContaminacionOut]


@router.get("/contaminacion/estaciones", response_model=ContaminacionResponse)
def get_contaminacion_estaciones(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    items = logica.obtener_contaminacion_por_estaciones(db, limit=limit)
    return {"count": len(items), "items": items}
