"""recompensas_api.py
@Author: Ariel Bejaran
@Date: 2024-06-15
@Description: API endpoints for managing user rewards in the web application.

"""

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from ..db.database import get_db
from sqlalchemy.orm import Session
from ..logic.recompensas_logic import RecompensasLogic
from ..db.models import Recompensa as RecompensaDB
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
    fecha_actualizacion: datetime.datetime | None = None #esto puedo causar problemas?
    
    
class RecompensaCreate(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=100)
    descripcion: str = Field(..., min_length=10, max_length=500)
    criterio_num_km: float = Field(..., gt=0, le=500)
    fecha_inicio: datetime.datetime
    fecha_fin: datetime.datetime
    
class RecompensaUpdate(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=100)
    descripcion: str = Field(..., min_length=10, max_length=500)
    criterio_num_km: float = Field(..., gt=0, le=500)
    fecha_inicio: datetime.datetime
    fecha_fin: datetime.datetime

    
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
    
    
@router.get("/recompensas_obtenidas", response_model=dict) 

def obtener_recompensas_con_progreso(db: Session = Depends(get_db),current_user: Usuario = Depends(get_current_user)):
    """
    Obtiene las recompensas obtenidas y las próximas recompensas para el usuario actual.
    """
    try:
        logica = RecompensasLogic()
        # Esta llamada ahora devuelve el objeto {obtenidas: [], proximas: []}
        return logica.procesar_y_obtener_recompensas(db, current_user.usuario_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/obtener_distancia_acumulada", response_model=Recompensa_Usuario)
def obtener_distancia_acumulada_este_mes(
    db: Session = Depends(get_db),
    usuario_id: str | None = None,
    authorization: str | None = Header(default=None),
):
    try:
        logica = RecompensasLogic()
        
        # Resolución de usuario (se mantiene igual)
        if usuario_id:
            usuario = db.query(Usuario).filter(Usuario.usuario_id == usuario_id).first()
            if not usuario:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
        else:
            usuario = get_current_user(authorization, db)

        km_mes = logica.obtener_distancia_total_mes_actual(db, usuario.usuario_id)

        return Recompensa_Usuario(
            usuario_id=usuario.usuario_id,
            km_acumulados=km_mes  # Antes tenías km_acumulados_este_mes (esto causaba el 500)
        )
        
    except Exception as e:
        # Imprime el error en la consola del servidor para ver qué falla exactamente
        print(f"DEBUG ERROR: {e}") 
        raise HTTPException(status_code=500, detail=f"Error al obtener distancia: {str(e)}")
    
    #--------------------------------------------------------


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
    
    
@router.put("/actualizar/{recompensa_id}", response_model=RecompensaResponse)
def actualizar_recompensa(
    recompensa_id: str,
    recompensa_update: RecompensaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza una recompensa existente (solo administradores).
    """
    try:
        # Validar permisos
        if not any(rol.nombre == "admin" for rol in current_user.roles):
            raise HTTPException(status_code=403, detail="No tienes permisos para actualizar recompensas")
        
        # Buscar recompensa
        recompensa = db.query(RecompensaDB).filter(RecompensaDB.recompensa_id == recompensa_id).first()
        if not recompensa:
            raise HTTPException(status_code=404, detail="Recompensa no encontrada")
        
        # Validar fechas
        if recompensa_update.fecha_fin <= recompensa_update.fecha_inicio:
            raise HTTPException(status_code=400, detail="La fecha de fin debe ser posterior a la de inicio")
        
        # Actualizar campos
        recompensa.titulo = recompensa_update.titulo
        recompensa.descripcion = recompensa_update.descripcion
        recompensa.criterio_num_km = recompensa_update.criterio_num_km
        recompensa.fecha_inicio = recompensa_update.fecha_inicio
        recompensa.fecha_fin = recompensa_update.fecha_fin
        
        db.commit()
        db.refresh(recompensa)
        
        return recompensa
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar recompensa: {str(e)}")
    
        #--------------------------------------------------------
        
        
#=================================
# Rutas POST (Crear)
#=================================

@router.post("/crear", response_model=RecompensaResponse, status_code=201)
def crear_recompensa(
    recompensa: RecompensaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea una nueva recompensa (solo administradores).
    """
    try:
        # Validar que el usuario sea admin
        if not any(rol.nombre == "admin" for rol in current_user.roles):
            raise HTTPException(status_code=403, detail="No tienes permisos para crear recompensas")
        
        # Validar que fecha_fin > fecha_inicio
        if recompensa.fecha_fin <= recompensa.fecha_inicio:
            raise HTTPException(status_code=400, detail="La fecha de fin debe ser posterior a la de inicio")
        
        # Crear nueva recompensa
        nueva_recompensa = RecompensaDB(
            recompensa_id=str(uuid.uuid4()),
            titulo=recompensa.titulo,
            descripcion=recompensa.descripcion,
            criterio_num_km=recompensa.criterio_num_km,
            fecha_inicio=recompensa.fecha_inicio,
            fecha_fin=recompensa.fecha_fin
        )
        
        db.add(nueva_recompensa)
        db.commit()
        db.refresh(nueva_recompensa)
        
        return nueva_recompensa
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear recompensa: {str(e)}")

#=================================
# Rutas DELETE (Eliminar)
#=================================

@router.delete("/eliminar/{recompensa_id}", status_code=204)
def eliminar_recompensa(
    recompensa_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Elimina una recompensa (solo administradores).
    """
    try:
        # Validar permisos
        if not any(rol.nombre == "admin" for rol in current_user.roles):
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar recompensas")
        
        # Buscar recompensa
        recompensa = db.query(RecompensaDB).filter(RecompensaDB.recompensa_id == recompensa_id).first()
        if not recompensa:
            raise HTTPException(status_code=404, detail="Recompensa no encontrada")
        
        # Eliminar
        db.delete(recompensa)
        db.commit()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar recompensa: {str(e)}")