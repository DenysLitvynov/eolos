"""
Autor: jinwei
Fecha: 26-10-2025
Descripción: API de perfil (GET/PUT) usando autenticación JWT Bearer.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, field_validator
import os, jwt

from ..db.database import get_db
from ..db.models import Usuario
from ..logic.perfil_logic import LogicaPerfil

router = APIRouter()
logica = LogicaPerfil()

# ====== Configuración JWT ======
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

if not JWT_SECRET:
    raise RuntimeError("Falta JWT_SECRET en las variables de entorno")


# ====== Esquemas Pydantic ======

class PerfilOut(BaseModel):
    """Modelo de salida del perfil (datos visibles del usuario)."""
    usuario_id: str
    targeta_id: str | None = None
    nombre: str | None = None
    apellido: str | None = None
    correo: EmailStr | None = None

    class Config:
        from_attributes = True


class PerfilUpdateIn(BaseModel):
    """
    Datos que el usuario puede editar en su perfil.
    - Siempre debe enviar la contraseña actual para confirmar los cambios.
    - La contraseña nueva es opcional.
    """

    nombre: str | None = Field(default=None, max_length=120)
    apellido: str | None = Field(default=None, max_length=120)
    correo: EmailStr | None = None
    targeta_id: str | None = Field(default=None, max_length=9)

    contrasena_actual: str = Field(..., min_length=8)
    contrasena_nueva: str | None = Field(default=None, min_length=8)

    @field_validator("targeta_id", mode="before")
    @classmethod
    def normalizar_targeta(cls, v):
        if v is None:
            return None
        v = str(v).strip()
        return None if v == "" or v.lower() == "null" else v


# ====== Helper de autenticación ======

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


# ====== Rutas ======

@router.get("/perfil", response_model=PerfilOut)
def read_perfil(current_user: Usuario = Depends(get_current_user)) -> PerfilOut:
    """Devuelve los datos del perfil del usuario autenticado."""

    return PerfilOut.model_validate(current_user)


@router.put("/perfil", response_model=PerfilOut)
def update_perfil(
    data: PerfilUpdateIn,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> PerfilOut:
    """Actualiza los datos del perfil."""

    try:
        usuario = logica.actualizar_perfil(
            db,
            usuario_id=str(current_user.usuario_id),
            nombre=data.nombre,
            apellido=data.apellido,
            correo=data.correo,
            targeta_id=data.targeta_id,
            contrasena_actual=data.contrasena_actual,
            contrasena_nueva=data.contrasena_nueva,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return PerfilOut.model_validate(usuario)

