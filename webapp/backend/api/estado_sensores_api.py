"""
Autor: Víctor Morant
Fecha: 20-11-2025
Descripción: Rutas para estado de sensores (bicicletas).
"""

# ---------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..logic.estado_sensores import LogicaEstadoSensores
from ..db.database import get_db
from sqlalchemy.orm import Session

# ---------------------------------------------------------

router = APIRouter(prefix="/estado-sensores")

class BikeResponse(BaseModel):
    id: str
    placa_id: str
    estado: str
    ultimaActualizacion: str
    parada: str

class MedicionResponse(BaseModel):
    lectura_id: str
    valor: float
    fecha_hora: str
    tipo: str
    lat: Optional[float]
    lon: Optional[float]
    es_anomalo: bool

class MensajeResponse(BaseModel):
    mensaje: str
    cantidad: Optional[int] = None

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

@router.get("/mediciones/{placa_id}")
def ruta_obtener_mediciones(
    placa_id: str,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las mediciones de una placa con rango de fechas opcional.
    Marca las mediciones anómalas (< 0 o > 200).
    """
    try:
        logica = LogicaEstadoSensores()
        resultado = logica.obtener_mediciones_placa(db, placa_id, fecha_inicio, fecha_fin)
        return [MedicionResponse(**med) for med in resultado]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

@router.delete("/mediciones/{lectura_id}")
def ruta_eliminar_medicion(lectura_id: str, db: Session = Depends(get_db)):
    """
    Elimina una medición específica por su ID.
    """
    try:
        logica = LogicaEstadoSensores()
        resultado = logica.eliminar_medicion(db, lectura_id)
        return MensajeResponse(**resultado)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

@router.delete("/mediciones-anomalas/{placa_id}")
def ruta_eliminar_mediciones_anomalas(placa_id: str, db: Session = Depends(get_db)):
    """
    Elimina todas las mediciones anómalas (< 0 o > 200) de una placa.
    """
    try:
        logica = LogicaEstadoSensores()
        resultado = logica.eliminar_mediciones_anomalas(db, placa_id)
        return MensajeResponse(**resultado)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# ---------------------------------------------------------