"""
Autor: jinwei
Fecha: 26-10-2025
Descripción: API de perfil (GET/PUT) usando autenticación JWT Bearer.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date, datetime
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
    rol_id: int | None = None
    nombre: str | None = None
    # 'apellido' se mantiene por compatibilidad, aunque el frontend ya no lo usa
    apellido: str | None = None
    correo: EmailStr | None = None
    fecha_registro: date | None = None

    class Config:
        from_attributes = True


class PerfilUpdateIn(BaseModel):
    """
    Modelo de entrada para la actualización del perfil.
    Solo se incluyen los campos que el usuario puede editar.
    """
    nombre: str | None = Field(default=None, max_length=120)
    # 'apellido' ya no se utiliza en frontend, pero se conserva temporalmente
    apellido: str | None = Field(default=None, max_length=120)
    correo: EmailStr | None = None
    # targeta_id: máximo 9 caracteres, str | None
    targeta_id: str | None = Field(default=None, max_length=9)
    contrasena: str | None = Field(default=None, min_length=6)

    # Normaliza valores vacíos como "", "null", etc., convirtiéndolos en None
    @field_validator("targeta_id", mode="before")
    @classmethod
    def normalizar_targeta(cls, v):
        if v is None:
            return None
        v = str(v).strip()
        if v == "" or v.lower() == "null":
            return None
        return v


# ====== Helper de autenticación ======

def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Usuario:
    """
    Extrae el usuario autenticado desde el token JWT enviado en el header Authorization.
    Valida:
      - Presencia del token
      - Formato Bearer
      - Firma y expiración
      - Existencia del usuario en la base de datos
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
    Devuelve la información del perfil del usuario autenticado.
    Ruta: GET /perfil
    """
    out = PerfilOut.model_validate(current_user)

    # Convertir datetime → date si es necesario (evita problemas de serialización)
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
    Actualiza el perfil del usuario autenticado.
    Ruta: PUT /perfil

    Campos permitidos:
      - nombre
      - apellido (aunque ya no se usa)
      - correo
      - targeta_id
      - contrasena (se encripta automáticamente)

    Si algún dato es inválido, se devuelve un error 400.
    """
    try:
        usuario = logica.actualizar_perfil(
            db,
            usuario_id=str(current_user.usuario_id),
            nombre=data.nombre,
            apellido=data.apellido,
            correo=data.correo,
            targeta_id=data.targeta_id,   # Ya pasó por el validador
            contrasena=data.contrasena,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    out = PerfilOut.model_validate(usuario)

    # Normalizar fecha_registro si es datetime
    if isinstance(getattr(usuario, "fecha_registro", None), datetime):
        out.fecha_registro = usuario.fecha_registro.date()

    return out
