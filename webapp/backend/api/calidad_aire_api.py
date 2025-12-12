"""
Autor: Víctor Morant
Fecha: 20-11-2025
Descripción: Rutas para calidad del aire.
"""

# ---------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..logic.calidad_aire import LogicaCalidadAire
from ..db.database import get_db
from sqlalchemy.orm import Session

# ---------------------------------------------------------

router = APIRouter(prefix="/calidad-aire")

class AQIResponse(BaseModel):
    aqi: int
    fecha_hora: str

class HistoricoResponse(BaseModel):
    valor: float
    fecha_hora: str
    aqi: int

# ---------------------------------------------------------

@router.get("/aqi/{placa_id}")
def ruta_obtener_aqi(placa_id: str, db: Session = Depends(get_db)):
    """
    Obtiene el AQI más reciente para una placa específica.
    """
    try:
        logica = LogicaCalidadAire()
        resultado = logica.obtener_aqi_reciente(db, placa_id)
        return AQIResponse(**resultado)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historico-24h/{placa_id}")
def ruta_obtener_historico(placa_id: str, db: Session = Depends(get_db)):
    """
    Obtiene todas las mediciones de las últimas 24 horas.
    """
    try:
        logica = LogicaCalidadAire()
        resultado = logica.obtener_historico_24h(db, placa_id)
        return [HistoricoResponse(**item) for item in resultado]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mediciones/{placa_id}")
def ruta_obtener_mediciones(placa_id: str, db: Session = Depends(get_db)):
    """
    Obtiene TODAS las mediciones de una placa (sin límite temporal).
    """
    try:
        logica = LogicaCalidadAire()
        resultado = logica.obtener_todas_mediciones(db, placa_id)
        return [HistoricoResponse(**item) for item in resultado]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------