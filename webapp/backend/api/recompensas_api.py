"""recompensas_api.py
@Author: Ariel Bejaran
@Date: 2024-06-15
@Description: API endpoints for managing user rewards in the web application.

"""

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from ..db.database import get_db
from sqlalchemy.orm import Session
from ..logic.recompensas_logic import RecompensasLogic
from ..pojos.recompensa import Recompensa
from ..db.models import Usuario # Para tipado de la dependencia
import datetime
from typing import List
from ..api.perfil_api import get_current_user # <<< DEBES REEMPLAZAR ESTA LÍNEA CON TU RUTA REAL


import uuid

router = APIRouter(prefix="/recompensas")  # Prefijo común para todas las rutas de la API

class RecompensaResponse(BaseModel):
    # recompensa_id es UUID en DB, se serializa como string en JSON.
    recompensa_id: uuid.UUID 
    titulo: str
    descripcion: str
    fecha_inicio: datetime.datetime
    fecha_fin: datetime.datetime
    criterio_num_km: float
    
class Recompensa_Usuario(BaseModel):
    usuario_id: str
    km_acumulados: float
    fecha_actualizacion: datetime.datetime = datetime.datetime.now() # Metadato
    
#=================================
# Rutas GET
#=================================

@router.get("/obtener_recompensas", response_model=List[RecompensaResponse])
def obtener_recompensas(db: Session = Depends(get_db)):
    """
    Obtiene la lista todas las recompensas disponibles.
    """
    try:
        logica = RecompensasLogic()
        # La lógica devuelve una lista de diccionarios, que FastAPI puede usar
        recompensas_data = logica.obtener_recompensas(db) 
        
        return recompensas_data
        
    except RuntimeError as e:
        # Usa 500 para errores internos del servidor
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Manejo de cualquier otra excepción no esperada
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
    
@router.get("/recompensas_obtenidas", response_model=List[dict])
def obtener_recompensas_con_progreso(
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user)
    ):
        """
        Devuelve la lista de recompensas indicando cuáles ha superado el usuario
        según su distancia recorrida en el mes.
        """
        try:
            logica = RecompensasLogic()
            return logica.obtener_estado_recompensas_usuario(db, current_user.usuario_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
# ---------------------------------------------------------


@router.get("/obtener_distancia_acumulada", response_model=Recompensa_Usuario)
def obtener_distancia_acumulada_este_mes(
    db: Session = Depends(get_db),
    usuario_id: str | None = None,
    authorization: str | None = Header(default=None),
):
    """
    Obtiene la distancia total recorrida por el usuario logeado en el mes actual.
    Ruta Final: /api/v1/recompensas/distancia-mensual
    """
    try:
        logica = RecompensasLogic()
        
        # Resolver usuario: si se pasa `usuario_id` por query param lo usamos (útil para pruebas),
        # en caso contrario intentamos autenticar con el token Bearer usando `get_current_user`.
        if usuario_id:
            usuario = db.query(Usuario).filter(Usuario.usuario_id == usuario_id).first()
            if not usuario:
                raise HTTPException(status_code=404, detail="Usuario no encontrado por usuario_id")
        else:
            # Esto lanzará HTTPException(401) si la cabecera falta o el token es inválido.
            usuario = get_current_user(authorization, db)

        km_mes = logica.obtener_distancia_total_mes_actual(db, usuario.usuario_id)

        return Recompensa_Usuario(
            usuario_id=usuario.usuario_id,
            km_acumulados_este_mes=km_mes
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener distancia: {str(e)}")


#=================================
# Rutas PUT
#=================================
@router.put("/actualizar_distancia_acumulada", response_model=Recompensa_Usuario)
def actualizar_distancia_acumulada_mensual(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user) # Usuario logeado
):
    """
    Calcula la distancia de los trayectos del mes actual y actualiza el campo 
    km_acumulados en la tabla recompensas_usuario.
    Ruta Final: /api/v1/recompensas/actualizar-distancia
    """
    try:
        logica = RecompensasLogic()
        
        # Llama a la nueva lógica que calcula y persiste el valor mensual
        km_actualizado = logica.actualizar_km_acumulados_este_mes(
            db, 
            current_user.usuario_id
        )
        
        return Recompensa_Usuario(
            usuario_id=current_user.usuario_id,
            km_acumulados_este_mes=km_actualizado
        )
        
    except Exception as e:
        # En caso de error, se lanza un 500 y se revierte la transacción.
        raise HTTPException(status_code=500, detail=f"Error al actualizar la distancia: {str(e)}")