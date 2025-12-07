"""
Autor: Ariel Bejaran
Fecha: 05-12-2025
Descripción: API auxiliares para la gestión de incidencias (lista simplificada para frontend).
Se reutiliza `LogicaIncidencias` y `get_current_user` para devolver una lista de incidencias
en un formato amigable para el frontend de `gestion_incidencias`.
"""

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import Incidencia, EstadoIncidencia,FuenteReporte
from ..logic.incidencias_logic import LogicaIncidencias
from ..logic.gestion_incidencias_logic import GestionIncidenciasLogic
from .perfil_api import get_current_user

router = APIRouter(prefix="/gestion-incidencias")
logica = LogicaIncidencias()
gestion_logic = GestionIncidenciasLogic()


class IncidenciaListadoOut(BaseModel):
    incidencia_id: str
    titulo: str
    tiempo: str
    fuente: str
    esResuelto: bool

#=====================================================================================================================================================
# FUNCIONES 
#=====================================================================================================================================================

def _formatear_tiempo_relativo(fecha_reporte: datetime) -> str:
    """Devuelve una cadena simple tipo '5min', '1h 30min' o fecha.
    Se usa para mostrar en las tarjetas del frontend.
    """
    try:
        ahora = datetime.now(timezone.utc)
        # Asegurar ambos con tzinfo para poder restar
        if fecha_reporte.tzinfo is None:
            fecha_reporte = fecha_reporte.replace(tzinfo=timezone.utc)
        delta = ahora - fecha_reporte
        segundos = int(delta.total_seconds())
    except Exception:
        return "hace un momento"

    if segundos < 60:
        return "Hace: justo ahora"
    minutos = segundos // 60
    if minutos < 60:
        return f"Hace: {minutos}min"
    horas = minutos // 60
    minutos_rest = minutos % 60
    if horas < 24:
        if minutos_rest == 0:
            return f"Hace: {horas}h"
        return f"Hace: {horas}h {minutos_rest}min"
    # Más de un día: devolver fecha en formato ISO corto
    return fecha_reporte.strftime("%Y-%m-%d")

#=====================================================================================================================================================
#RUTAS
#=====================================================================================================================================================

## ➡️ NUEVA RUTA: Filtrada por Rol (Admin/Técnico)
@router.get("/admin_tecnico", response_model=List[IncidenciaListadoOut])
def listar_incidencias_filtradas_por_rol(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> List[IncidenciaListadoOut]:
    """
    Ruta que devuelve incidencias filtradas según el rol del usuario:
    - Admin: Fuentes 'app' o 'web'.
    - Tecnico: Fuente 'parada_bici'.
    - Otros: Lista vacía.
    
    Ruta montada como: GET /api/v1/gestion-incidencias/filtradas
    """
    
    # 1. Obtener nombres de roles desde current_user.roles (relación SQLAlchemy)
    try:
        role_names = [r.nombre for r in getattr(current_user, 'roles', [])]
    except Exception:
        role_names = []

    print(f"[DEBUG] Usuario: {current_user.correo}, Roles: {role_names}")  # Log para depuración
    
    # 2. Definir los filtros según el rol
    incidencias = []
    
    if 'admin' in role_names:
        # Admin ve incidencias de app, web o admin
        fuentes_filtrar = [FuenteReporte.app, FuenteReporte.web, FuenteReporte.admin]
        try:
            incidencias = gestion_logic.listar_incidencias_por_fuente(db, fuentes_filtrar)
        except Exception as e:
            print(f"Error filtrando por fuente (admin): {e}")
            raise HTTPException(status_code=500, detail=str(e))
        
    elif 'tecnico' in role_names:
        # Técnico ve incidencias vinculadas a bicicletas
        try:
            incidencias = db.query(Incidencia).filter(Incidencia.bicicleta_id != None).order_by(Incidencia.fecha_reporte.desc()).all()
        except Exception as e:
            print(f"Error filtrando incidencias de técnico: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Si el rol no es admin ni tecnico, retorna lista vacía
        print(f"[DEBUG] Usuario no es admin ni tecnico, retornando lista vacía")
        return []

    # 3. Formatear el resultado
    resultado = []
    for inc in incidencias:
        titulo = inc.descripcion if getattr(inc, "descripcion", None) else "Incidencia sin descripción"
        tiempo = _formatear_tiempo_relativo(inc.fecha_reporte) if getattr(inc, "fecha_reporte", None) else "Hace: ahora"
        # Usamos .value para obtener el string del Enum (si es un Enum)
        fuente = getattr(inc.fuente, 'value', str(inc.fuente)) if inc.fuente is not None else "app" 
        es_resuelto = (inc.estado.name == 'resuelto') if hasattr(inc.estado, 'name') else (inc.estado == 'resuelto')

        resultado.append(
            IncidenciaListadoOut(
                incidencia_id=getattr(inc, 'incidencia_id', None),
                titulo=titulo,
                tiempo=tiempo,
                fuente=fuente.title(),
                esResuelto=es_resuelto,
            )
        )

    print(f"[DEBUG] Retornando {len(resultado)} incidencias filtradas")
    return resultado

@router.post("/cambiar_estado", response_model=IncidenciaListadoOut)
def cambiar_estado_incidencia( 
    incidencia_id: str,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> IncidenciaListadoOut:
    """
    Cambia el estado de una incidencia dada.
    
    Ruta montada como: POST /api/v1/gestion-incidencias/cambiar_estado
    """
    try:
        incidencia_actualizada = gestion_logic.cambiar_estado_incidencia(db, incidencia_id, nuevo_estado)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    titulo = incidencia_actualizada.descripcion if getattr(incidencia_actualizada, "descripcion", None) else "Incidencia"
    tiempo = _formatear_tiempo_relativo(incidencia_actualizada.fecha_reporte) if getattr(incidencia_actualizada, "fecha_reporte", None) else "Hace: ahora"
    fuente = getattr(incidencia_actualizada.fuente, 'value', str(incidencia_actualizada.fuente)) if incidencia_actualizada.fuente is not None else "app"
    es_resuelto = (incidencia_actualizada.estado.name == 'resuelto') if hasattr(incidencia_actualizada.estado, 'name') else (incidencia_actualizada.estado == 'resuelto')

    return IncidenciaListadoOut(
        incidencia_id=getattr(incidencia_actualizada, 'incidencia_id', None),
        titulo=titulo,
        tiempo=tiempo,
        fuente=fuente.title(),
        esResuelto=es_resuelto,
    )


## ➡️ RUTA /public (Se mantiene para pruebas sin autenticación)
@router.get("/public", response_model=List[IncidenciaListadoOut])
def listar_incidencias_publicas(
     db: Session = Depends(get_db),
) -> List[IncidenciaListadoOut]:
    """Endpoint público de solo-lectura para pruebas en frontend."""
    # ... (El código de la ruta /public se mantiene igual) ...
    try:
        incidencias = gestion_logic.listar_todas_incidencias(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # ... (El código de formateo del resultado se mantiene igual) ...
    resultado = []
    for inc in incidencias:
        titulo = inc.descripcion if getattr(inc, "descripcion", None) else "Incidencia"
        tiempo = _formatear_tiempo_relativo(inc.fecha_reporte) if getattr(inc, "fecha_reporte", None) else "Hace: ahora"
        fuente = getattr(inc.fuente, 'value', str(inc.fuente)) if inc.fuente is not None else "app"
        es_resuelto = (inc.estado.name == 'resuelto') if hasattr(inc.estado, 'name') else (inc.estado == 'resuelto')

        resultado.append(
            IncidenciaListadoOut(
                incidencia_id=getattr(inc, 'incidencia_id', None),
                titulo=titulo,
                tiempo=tiempo,
                fuente=fuente.title(),
                esResuelto=es_resuelto,
            )
        )

    return resultado