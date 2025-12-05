# File: backend/api/mapas_api.py
"""
Autor: Denys Litvynov Lymanets
Fecha: 04-12-2025
Descripción: Rutas API para mapas.
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import date, datetime  # <--- Añade datetime aquí
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..logic.mapas import LogicaMapas
from ..pojos.posicion_gps import PosicionGPS

router = APIRouter(prefix="/mapas", tags=["mapas"])

# File: backend/api/mapas_api.py
@router.get("/obtener-mapa")
def obtener_mapa(
    tipo: str,  # ← ahora aceptamos "general", "pm25", "pm10", "no2", "o3"
    dia: date,
    lat_min: float,
    lon_min: float,
    lat_max: float,
    lon_max: float,
    db: Session = Depends(get_db)
):
    try:
        logica = LogicaMapas()
        inf_izq = PosicionGPS(lat_min, lon_min)
        sup_der = PosicionGPS(lat_max, lon_max)
        
        # Normalizamos el tipo para que coincida con el enum
        tipo_normalizado = tipo
        if tipo == "pm25":
            tipo_normalizado = "pm2_5"
        elif tipo == "general":
            tipo_normalizado = "general"  # lo dejamos tal cual

        result = logica.obtener_mapa_de_tipo_de_dia_de_destino(
            db, tipo_normalizado, datetime.combine(dia, datetime.min.time()), inf_izq, sup_der
        )
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------
