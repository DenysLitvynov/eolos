"""
Autor: Denys Litvynov Lymanets
Fecha: 19-11-2025
Descripción: Rutas API para trayectos.
"""

# ---------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
# ---------------------------------------------------------
from ..db.database import get_db
from ..logic.trayectos import LogicaTrayectos
from ..pojos.posicion_gps import PosicionGPS
from ..pojos.medida import Medida as DTOMedida
from ..db.models import TipoMedidaEnum, EstadoBicicleta
# ---------------------------------------------------------

router = APIRouter(prefix="/trayectos", tags=["trayectos"])

# ---------------------------------------------------------
# Models Pydantic
# ---------------------------------------------------------
class PosicionGPSRequest(BaseModel):
    lat: float
    lon: float

class IniciarTrayectoRequest(BaseModel):
    targeta_id: str
    bicicleta_id: str
    fecha_inicio: datetime
    origen: PosicionGPSRequest

class ObtenerDatosTrayectoResponse(BaseModel):
    usuario_id: str
    placa_id: str

class FinalizarTrayectoRequest(BaseModel):
    trayecto_id: str
    fecha_fin: datetime
    destino: PosicionGPSRequest

class GuardarMedidaRequest(BaseModel):
    trayecto_id: str
    placa_id: str
    tipo: TipoMedidaEnum
    valor: float
    fecha_hora: datetime
    posicion: PosicionGPSRequest

class ActualizarPlacaRequest(BaseModel):
    placa_id: str
    estado: str
    ult_actualizacion_estado: datetime

class ActualizarBiciRequest(BaseModel):
    bicicleta_id: str
    posicion: PosicionGPSRequest
    estado: EstadoBicicleta

class ComprobarEstacionRequest(BaseModel):
    posicion: PosicionGPSRequest

# ---------------------------------------------------------
# Ruta: iniciar_trayecto
# ---------------------------------------------------------
@router.post("/iniciar-trayecto")
def iniciar_trayecto(data: IniciarTrayectoRequest, db: Session = Depends(get_db)):
    """
    Inicia un trayecto para un usuario con una bicicleta específica.

    Args:
        data (IniciarTrayectoRequest): Datos de inicio de trayecto (targeta_id, bicicleta_id, fecha, origen).
        db (Session): Sesión de base de datos.

    Returns:
        dict: Diccionario con trayecto_id generado.
    """
    try:
        logica = LogicaTrayectos()
        origen = PosicionGPS(data.origen.lat, data.origen.lon)
        trayecto_id = logica.iniciar_trayecto(db, data.targeta_id, data.bicicleta_id, data.fecha_inicio, origen)
        return {"trayecto_id": trayecto_id}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(500, str(e))

# ---------------------------------------------------------
# Ruta: obtener_datos_trayecto
# ---------------------------------------------------------
@router.get("/obtener-datos-trayecto/{trayecto_id}")
def obtener_datos_trayecto(trayecto_id: str, db: Session = Depends(get_db)):
    """
    Obtiene los datos de un trayecto específico.

    Args:
        trayecto_id (str): ID del trayecto.
        db (Session): Sesión de base de datos.

    Returns:
        ObtenerDatosTrayectoResponse: Objeto con usuario_id y placa_id.
    """
    try:
        logica = LogicaTrayectos()
        usuario_id, placa_id = logica.obtener_datos_trayecto(db, trayecto_id)
        return ObtenerDatosTrayectoResponse(usuario_id=usuario_id, placa_id=placa_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(500, str(e))

# ---------------------------------------------------------
# Ruta: finalizar_trayecto
# ---------------------------------------------------------
@router.put("/finalizar-trayecto")
def finalizar_trayecto(data: FinalizarTrayectoRequest, db: Session = Depends(get_db)):
    """
    Finaliza un trayecto existente y calcula información final.

    Args:
        data (FinalizarTrayectoRequest): Datos para finalizar el trayecto (trayecto_id, fecha_fin, destino).
        db (Session): Sesión de base de datos.

    Returns:
        dict: Diccionario con mensaje de resultado.
    """
    try:
        logica = LogicaTrayectos()
        destino = PosicionGPS(data.destino.lat, data.destino.lon)
        result = logica.finalizar_trayecto(db, data.trayecto_id, data.fecha_fin, destino)
        return {"mensaje": result}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(500, str(e))

# ---------------------------------------------------------
# Ruta: guardar_medida
# ---------------------------------------------------------
@router.post("/guardar-medida")
def guardar_medida(data: GuardarMedidaRequest, db: Session = Depends(get_db)):
    """
    Guarda una medida asociada a un trayecto y una placa.

    Args:
        data (GuardarMedidaRequest): Datos de la medida (trayecto_id, placa_id, tipo, valor, fecha_hora, posicion).
        db (Session): Sesión de base de datos.

    Returns:
        dict: Diccionario con mensaje de resultado.
    """
    try:
        logica = LogicaTrayectos()
        posicion = PosicionGPS(data.posicion.lat, data.posicion.lon)
        medida = DTOMedida(data.trayecto_id, data.placa_id, data.tipo, data.valor, data.fecha_hora, posicion)
        result = logica.guardar_medida(db, medida)
        return {"mensaje": result}
    except RuntimeError as e:
        raise HTTPException(500, str(e))

# ---------------------------------------------------------
# Ruta: actualizar_estado_placa
# ---------------------------------------------------------
@router.put("/actualizar-estado-placa")
def actualizar_estado_placa(data: ActualizarPlacaRequest, db: Session = Depends(get_db)):
    """
    Actualiza el estado de una placa de sensores.

    Args:
        data (ActualizarPlacaRequest): Datos de la placa (placa_id, estado, ult_actualizacion_estado).
        db (Session): Sesión de base de datos.

    Returns:
        dict: Diccionario con mensaje de resultado.
    """
    try:
        logica = LogicaTrayectos()
        result = logica.actualizar_estado_placa(db, data.placa_id, data.estado, data.ult_actualizacion_estado)
        return {"mensaje": result}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(500, str(e))

# ---------------------------------------------------------
# Ruta: actualizar_estado_bici
# ---------------------------------------------------------
@router.put("/actualizar-estado-bici")
def actualizar_estado_bici(data: ActualizarBiciRequest, db: Session = Depends(get_db)):
    """
    Actualiza el estado y posición de una bicicleta.

    Args:
        data (ActualizarBiciRequest): Datos de la bicicleta (bicicleta_id, posicion, estado).
        db (Session): Sesión de base de datos.

    Returns:
        dict: Diccionario con mensaje de resultado.
    """
    try:
        logica = LogicaTrayectos()
        posicion = PosicionGPS(data.posicion.lat, data.posicion.lon)
        result = logica.actualizar_estado_bici(db, data.bicicleta_id, posicion, data.estado)
        return {"mensaje": result}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(500, str(e))

# ---------------------------------------------------------
# Ruta: comprobar_estacion_bici
# ---------------------------------------------------------
@router.post("/comprobar-estacion-bici")
def comprobar_estacion_bici(data: ComprobarEstacionRequest, db: Session = Depends(get_db)):
    """
    Comprueba si una bicicleta se encuentra cerca de una estación.

    Args:
        data (ComprobarEstacionRequest): Posición a comprobar.
        db (Session): Sesión de base de datos.

    Returns:
        dict: Diccionario con estacion_id (None si no hay coincidencia).
    """
    try:
        logica = LogicaTrayectos()
        posicion = PosicionGPS(data.posicion.lat, data.posicion.lon)
        estacion_id = logica.comprobar_estacion_bici(db, posicion)
        return {"estacion_id": estacion_id}
    except RuntimeError as e:
        raise HTTPException(500, str(e))
# ---------------------------------------------------------

