"""
Autor: JINWEI
Fecha: 21-12-2025
Descripción: Home API (landing registrado).

Notas:
- usuario_id SIEMPRE se obtiene desde el JWT (current_user)
- lat/lon son opcionales (GPS del cliente)
- La respuesta incluye km_resumen para renderizar la sección de KM en el frontend
"""

from __future__ import annotations

from typing import Optional, Any, Dict
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import Usuario
from ..logic.home_logic import LogicaHome
from .perfil_api import get_current_user  # reutiliza JWT

router = APIRouter()
logica = LogicaHome()


class UsuarioHomeOut(BaseModel):
    usuario_id: str
    nombre_visible: str = "Usuario"


class GasOut(BaseModel):
    tipo: str
    valor: Optional[float] = None
    unidad: Optional[str] = None


class NivelActualOut(BaseModel):
    gases: list[GasOut] = Field(default_factory=list)


class CalidadAireOut(BaseModel):
    score: Any = "--"
    estado: str = "Mala"
    descripcion: str = "No hay datos recientes de calidad del aire."
    fecha_hora: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class ImpactoOut(BaseModel):
    rutas_limpias: int = 0
    co2_kg: float = 0.0
    puntos: int = 0


class UltimoTrayectoOut(BaseModel):
    trayecto_id: str
    bicicleta_id: Optional[str] = None
    distancia_km: Optional[float] = None
    tiempo_min: Optional[int] = None
    calidad_promedio: Optional[str] = None


class KmResumenOut(BaseModel):
    km_acumulados: float = 0.0
    descuento_acumulado: float = 0.0
    base_price: float = 59.99
    usted_pagaria: float = 59.99


class HomeOut(BaseModel):
    usuario: UsuarioHomeOut
    placa_id: Optional[str] = None
    calidad_aire: CalidadAireOut
    nivel_actual: NivelActualOut
    impacto: ImpactoOut
    ultimo_trayecto: Optional[UltimoTrayectoOut] = None
    km_resumen: KmResumenOut


@router.get("/home", response_model=HomeOut)
def get_home(
    lat: float | None = Query(default=None),
    lon: float | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    data: Dict[str, Any] = logica.obtener_home(
        db,
        usuario_id=str(current_user.usuario_id),
        lat=lat,
        lon=lon,
    )

    # Safety net: 防止前端炸
    if "km_resumen" not in data or not isinstance(data.get("km_resumen"), dict):
        data["km_resumen"] = {
            "km_acumulados": 0.0,
            "descuento_acumulado": 0.0,
            "base_price": 59.99,
            "usted_pagaria": 59.99,
        }

    return data
