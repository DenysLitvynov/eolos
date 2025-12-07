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

# ---------------------------------------------------------