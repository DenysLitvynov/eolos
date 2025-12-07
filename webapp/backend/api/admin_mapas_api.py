"""
Autor: Denys Litvynov Lymanets
Fecha: 05-12-2025
Descripción: Rutas API REST para la gestión de mapas de administrador.
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import date, datetime
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..logic.logic_admin_mapas import LogicaAdminMapas

router = APIRouter(prefix="/admin-mapas", tags=["admin-mapas"])

# ---------------------------------------------------------
# Endpoint para obtener datos de mapa histórico (Admin)
# ---------------------------------------------------------
@router.get("/obtener-mapa-admin")
def obtener_mapa_admin(
    tipo: str,
    dia: date,
    lat_min: float,
    lon_min: float,
    lat_max: float,
    lon_max: float,
    db: Session = Depends(get_db)
):
    """
    Endpoint para recuperar datos de mapas históricos.
    
    Args:
        tipo (str): Tipo de contaminante.
        dia (date): Fecha de consulta.
        lat_min, lon_min, lat_max, lon_max (float): Coordenadas del bounding box.
        db (Session): Inyección de dependencia de BD.
        
    Returns:
        JSON con la estructura de datos del mapa.
    """
    try:
        logica = LogicaAdminMapas()
        # Convertimos date a datetime (inicio del día)
        fecha_dt = datetime.combine(dia, datetime.min.time())
        
        result = logica.obtener_mapa_admin(
            db, tipo, fecha_dt, lat_min, lon_min, lat_max, lon_max
        )
        return result
    except Exception as e:
        # En producción usar logger, aquí print para debug
        print(f"Error en admin-mapas: {e}")
        raise HTTPException(status_code=500, detail=str(e))
