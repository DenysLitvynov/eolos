"""
Autor:jinwei
Fecha: 26-10-2025
Descripción: API de perfil (GET/PUT) usando autenticación JWT Bearer.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
import os, jwt

from ..db.database import get_db
from ..db.models import Usuario
from ..logic.perfil_logic import LogicaPerfil

router = APIRouter()
logica = LogicaPerfil()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
if not JWT_SECRET:
    raise RuntimeError("Falta JWT_SECRET en las variables de entorno")


# ====== Esquemas Pydantic ======
class PerfilOut(BaseModel):
    """Modelo de salida del perfil (datos visibles del usuario)."""
    usuario_id: str
    targeta_id: str | None = None
    rol_id: int | None = None
    nombre: str | None = None
    apellido: str | None = None
    correo: EmailStr | None = None
    fecha_registro: date | None = None

    class Config:
        from_attributes = True


class PerfilUpdateIn(BaseModel):
    """Modelo de entrada para actualización del perfil (solo campos editables)."""
    nombre: str | None = Field(default=None, max_length=120)
    apellido: str | None = Field(default=None, max_length=120)
    correo: EmailStr | None = None
    targeta_id: str | None = Field(default=None, max_length=120)
    contrasena: str | None = Field(default=None, min_length=6)


# ====== Helper de autenticación ======
def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Usuario:
    """
    Extrae y valida el usuario actual a partir del token JWT Bearer.

    - Verifica que el encabezado Authorization exista y empiece con 'Bearer '.
    - Decodifica el token y obtiene el campo 'sub' (ID del usuario).
    - Lanza excepciones 401/404 si el token o usuario no son válidos.
    """
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
        raise HTTPException(status_code=401, detail="Token sin 'sub'")

    usuario = db.query(Usuario).filter(Usuario.usuario_id == str(usuario_id)).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


# ====== Rutas ======
@router.get("/perfil", response_model=PerfilOut)
def read_perfil(current_user: Usuario = Depends(get_current_user)) -> PerfilOut:
    """
    Devuelve la información del perfil del usuario autenticado (GET /perfil).
    """
    out = PerfilOut.model_validate(current_user)
    # Convertir datetime a date si es necesario
    if isinstance(getattr(current_user, "fecha_registro", None), datetime):
        out.fecha_registro = current_user.fecha_registro.date()
    return out


@router.put("/perfil", response_model=PerfilOut)
def update_perfil(
    data: PerfilUpdateIn,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> PerfilOut:
    """
    Actualiza los datos del perfil del usuario autenticado (PUT /perfil).

    Campos admitidos:
      - nombre, apellido, correo, targeta_id, contrasena
    La contraseña se encripta si se proporciona.
    """
    try:
        usuario = logica.actualizar_perfil(
            db,
            usuario_id=str(current_user.usuario_id),
            nombre=data.nombre,
            apellido=data.apellido,
            correo=data.correo,
            targeta_id=data.targeta_id,  # Mantener el mismo nombre de campo
            contrasena=data.contrasena,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    out = PerfilOut.model_validate(usuario)
    if isinstance(getattr(usuario, "fecha_registro", None), datetime):
        out.fecha_registro = usuario.fecha_registro.date()
    return out
