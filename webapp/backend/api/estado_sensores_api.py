"""
Autor: Víctor Morant
Fecha: 20-11-2025
Descripción: Rutas para estado de sensores (bicicletas).
"""

# ---------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..logic.estado_sensores import LogicaEstadoSensores
from ..db.database import get_db
from sqlalchemy.orm import Session

# ---------------------------------------------------------

router = APIRouter(prefix="/estado-sensores")

class BikeResponse(BaseModel):
    id: str
    estado: str
    ultimaActualizacion: str
    parada: str

# ---------------------------------------------------------

@router.get("/bicicletas")
def ruta_obtener_bicicletas(db: Session = Depends(get_db)):
    """
    Obtiene todas las bicicletas con su estado de sensor y información de estación.
    """
    try:
        logica = LogicaEstadoSensores()
        resultado = logica.obtener_todas_bicicletas(db)
        return [BikeResponse(**bike) for bike in resultado]
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# ---------------------------------------------------------