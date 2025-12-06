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
# NUEVO: Endpoint para forzar cálculo de calidad general
# ---------------------------------------------------------
from ..logic.mapas import LogicaMapas
from ..pojos.posicion_gps import PosicionGPS
from datetime import datetime, timezone

@router.post("/calcular-general")
def calcular_general(db: Session = Depends(get_db)):
    """
    Calcula y guarda la calidad general del aire para el día actual.
    Se basa en las medidas existentes.
    """
    try:
        logica = LogicaMapas()
        
        # Area aproximada de la ciudad (usando los defaults del frontend)
        # Lat: 38.98 - 39.03, Lon: -0.19 - -0.14
        inf_izq = PosicionGPS(38.9000, -0.2500) # Un poco mas amplio
        sup_der = PosicionGPS(39.1000, -0.1000)
        
        fecha_hoy = datetime.now(timezone.utc)
        
        # 1. Unificar medidas
        unified = logica.unificar_medidas_de_todos_tipos_de_dia(db, fecha_hoy, inf_izq, sup_der)
        
        # 2. Calcular y guardar
        res = logica.calcular_calidad_general_del_aire(db, unified, fecha_hoy)
        
        if res == "OK":
            return {"status": "success", "message": "Calidad general calculada correctamente."}
        else:
            raise HTTPException(status_code=500, detail=res)
            
    except Exception as e:
        print(f"Error calculating general quality: {e}")
        raise HTTPException(status_code=500, detail=str(e))