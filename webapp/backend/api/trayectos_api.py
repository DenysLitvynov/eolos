"""
Autor: Denys Litvynov Lymanets
Fecha: 19-11-2025
Descripción: Rutas API para trayectos.
"""

# ---------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
import os
import jwt
# ---------------------------------------------------------
from ..db.database import get_db
from ..db.models import Usuario
from ..logic.trayectos import LogicaTrayectos
from ..pojos.posicion_gps import PosicionGPS
from ..pojos.medida import Medida as DTOMedida
from ..db.models import TipoMedidaEnum, EstadoBicicleta
# ---------------------------------------------------------

# JWT config
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

if not JWT_SECRET:
    raise RuntimeError("Falta JWT_SECRET en las variables de entorno")

# ---------------------------------------------------------
# Helper de autenticación (igual a perfil_api.py)
# ---------------------------------------------------------

def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Usuario:

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Falta token Bearer")

    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

    usuario_id = payload.get("sub")
    if not usuario_id:
        raise HTTPException(status_code=401, detail="Token inválido (sin sub)")

    usuario = db.query(Usuario).filter(Usuario.usuario_id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return usuario

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
# Ruta: usuario/ultimo - Obtener último trayecto completado del usuario autenticado
# ---------------------------------------------------------

class TrayectoMedidaResponse(BaseModel):
    aqi: int
    fecha_hora: str
    valor: float

class UltimoTrayectoResponse(BaseModel):
    trayecto_id: str
    fecha_inicio: str
    fecha_fin: str | None
    distancia_total: float
    origen_estacion_id: str
    destino_estacion_id: str
    aqi_promedio: int
    aqi_maximo: int
    mediciones_count: int

@router.get("/usuario/ultimo", response_model=UltimoTrayectoResponse)
def obtener_ultimo_trayecto(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene el último trayecto completado del usuario autenticado.
    Solo retorna trayectos con fecha_fin (completados).
    
    Args:
        db (Session): Sesión de base de datos.
        current_user (Usuario): Usuario autenticado del token.
    
    Returns:
        UltimoTrayectoResponse: Datos del último trayecto con AQI promediado.
    """
    try:
        from ..db.models import Trayecto, Medida
        from ..logic.calidad_aire import LogicaCalidadAire
        
        # Obtener el último trayecto completado del usuario
        trayecto = db.query(Trayecto).filter(
            Trayecto.usuario_id == str(current_user.usuario_id),
            Trayecto.fecha_fin.isnot(None)  # Solo completados
        ).order_by(Trayecto.fecha_fin.desc()).first()
        
        if not trayecto:
            raise ValueError(f"No hay trayectos completados para el usuario {current_user.usuario_id}")
        
        # Obtener todas las mediciones asociadas al trayecto
        mediciones = db.query(Medida).filter(
            Medida.trayecto_id == trayecto.trayecto_id
        ).all()
        
        # Calcular AQI promedio y máximo (usando valores directamente como AQI)
        aqi_values = [m.valor for m in mediciones]
        aqi_promedio = int(sum(aqi_values) / len(aqi_values)) if aqi_values else 0
        aqi_maximo = int(max(aqi_values)) if aqi_values else 0
        
        return UltimoTrayectoResponse(
            trayecto_id=trayecto.trayecto_id,
            fecha_inicio=trayecto.fecha_inicio.isoformat(),
            fecha_fin=trayecto.fecha_fin.isoformat() if trayecto.fecha_fin else None,
            distancia_total=float(trayecto.distancia_total),
            origen_estacion_id=str(trayecto.origen_estacion_id),
            destino_estacion_id=str(trayecto.destino_estacion_id),
            aqi_promedio=aqi_promedio,
            aqi_maximo=aqi_maximo,
            mediciones_count=len(mediciones)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo trayecto: {str(e)}")

# ---------------------------------------------------------
# Ruta: trayectos/{trayecto_id}/mediciones - Obtener mediciones PM2.5 de un trayecto
# ---------------------------------------------------------

class MedicionPM25Response(BaseModel):
    valor: float
    fecha_hora: str
    aqi: int

@router.get("/{trayecto_id}/mediciones", response_model=list[MedicionPM25Response])
def obtener_mediciones_trayecto(
    trayecto_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las mediciones PM2.5 asociadas a un trayecto específico.
    
    Args:
        trayecto_id (str): ID del trayecto.
        db (Session): Sesión de base de datos.
    
    Returns:
        list[MedicionPM25Response]: Lista de mediciones PM2.5 ordenadas por fecha.
    """
    try:
        from ..db.models import Medida, TipoMedidaEnum
        from ..logic.calidad_aire import LogicaCalidadAire
        
        # Obtener todas las mediciones para el trayecto
        mediciones = db.query(Medida).filter(
            Medida.trayecto_id == trayecto_id
        ).order_by(Medida.fecha_hora.asc()).all()
        
        if not mediciones:
            raise ValueError(f"No hay mediciones para el trayecto {trayecto_id}")
        
        # Usar valores directamente como AQI (sin conversión)
        resultado = [
            MedicionPM25Response(
                valor=m.valor,
                fecha_hora=m.fecha_hora.isoformat(),
                aqi=int(m.valor)  # Usar el valor directamente como AQI
            )
            for m in mediciones
        ]
        
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo mediciones: {str(e)}")

# ---------------------------------------------------------
# Ruta: usuario/ultimos - Obtener últimos 10 trayectos completados del usuario autenticado
# ---------------------------------------------------------

class TrayectoListaResponse(BaseModel):
    trayecto_id: str
    fecha_inicio: str
    fecha_fin: str
    aqi_promedio: int
    aqi_maximo: int
    mediciones_count: int
    distancia_total: float
    origen_estacion_id: str
    destino_estacion_id: str

@router.get("/usuario/ultimos", response_model=list[TrayectoListaResponse])
def obtener_ultimos_trayectos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene los últimos 10 trayectos completados del usuario autenticado.
    Ordenados por fecha_fin descendente (más recientes primero).
    
    Args:
        db (Session): Sesión de base de datos.
        current_user (Usuario): Usuario autenticado del token.
    
    Returns:
        list[TrayectoListaResponse]: Lista de últimos 10 trayectos.
    """
    try:
        from ..db.models import Trayecto, Medida
        
        # Obtener últimos 10 trayectos completados del usuario
        trayectos = db.query(Trayecto).filter(
            Trayecto.usuario_id == str(current_user.usuario_id),
            Trayecto.fecha_fin.isnot(None)  # Solo completados
        ).order_by(Trayecto.fecha_fin.desc()).limit(10).all()
        
        if not trayectos:
            raise ValueError(f"No hay trayectos completados para el usuario {current_user.usuario_id}")
        
        resultado = []
        for trayecto in trayectos:
            # Obtener mediciones para cada trayecto
            mediciones = db.query(Medida).filter(
                Medida.trayecto_id == trayecto.trayecto_id
            ).all()
            
            # Calcular AQI promedio y máximo
            aqi_values = [m.valor for m in mediciones]
            aqi_promedio = int(sum(aqi_values) / len(aqi_values)) if aqi_values else 0
            aqi_maximo = int(max(aqi_values)) if aqi_values else 0
            
            resultado.append(TrayectoListaResponse(
                trayecto_id=trayecto.trayecto_id,
                fecha_inicio=trayecto.fecha_inicio.isoformat(),
                fecha_fin=trayecto.fecha_fin.isoformat(),
                aqi_promedio=aqi_promedio,
                aqi_maximo=aqi_maximo,
                mediciones_count=len(mediciones),
                distancia_total=float(trayecto.distancia_total),
                origen_estacion_id=str(trayecto.origen_estacion_id),
                destino_estacion_id=str(trayecto.destino_estacion_id)
            ))
        
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo trayectos: {str(e)}")

# ---------------------------------------------------------

