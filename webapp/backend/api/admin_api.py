"""
Autor: jinwei
Fecha: 07-12-2025
Descripción: API de administración de usuarios (listado / CRUD) usando JWT Bearer.
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Literal, Optional
import os, jwt

from ..db.database import get_db
from ..db.models import Usuario, Rol
from ..logic.admin_logic import LogicaAdmin

router = APIRouter(prefix="/admin_api", tags=["admin"])
logica = LogicaAdmin()

# ====== Configuración JWT ======
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

if not JWT_SECRET:
    raise RuntimeError("Falta JWT_SECRET en las variables de entorno")


# ====== Schemas ======

class UsuarioAdminOut(BaseModel):
    """Datos que ve el admin en la tabla."""
    usuario_id: str
    targeta_id: str | None = None
    nombre: str | None = None
    apellido: str | None = None
    correo: EmailStr | None = None
    rol: str | None = None

    class Config:
        from_attributes = True


class UsuarioAdminCreateIn(BaseModel):
    """Datos necesarios para crear un usuario desde el panel admin."""
    nombre: str = Field(..., max_length=120)
    apellido: str = Field(..., max_length=120)
    correo: EmailStr
    targeta_id: str | None = Field(default=None, max_length=36)
    rol: Literal["admin", "tecnico", "usuario"] = "usuario"
    contrasena: str = Field(..., min_length=8)

    @field_validator("targeta_id", mode="before")
    @classmethod
    def normalizar_targeta(cls, v):
        if v is None:
            return None
        v = str(v).strip()
        return None if v == "" or v.lower() == "null" else v


class UsuarioAdminUpdateIn(BaseModel):
    """Datos que puede modificar el admin (sin contraseña)."""
    nombre: str | None = Field(default=None, max_length=120)
    apellido: str | None = Field(default=None, max_length=120)
    correo: EmailStr | None = None
    targeta_id: str | None = Field(default=None, max_length=36)
    rol: Optional[Literal["admin", "tecnico", "usuario"]] = None

    @field_validator("targeta_id", mode="before")
    @classmethod
    def normalizar_targeta(cls, v):
        if v is None:
            return None
        v = str(v).strip()
        return None if v == "" or v.lower() == "null" else v


# ====== Auth helpers ======

def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Usuario:
    """Lee el token y devuelve un Usuario."""
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


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Solo acceso a admin."""
    roles = getattr(current_user, "roles", []) or []
    nombres = {r.nombre.lower() for r in roles if isinstance(r, Rol)}
    if "admin" not in nombres:
        raise HTTPException(status_code=403, detail="Permisos insuficientes (se requiere rol Admin)")
    return current_user


# ====== Rutas ======

@router.get("/usuarios", response_model=List[UsuarioAdminOut])
def listar_usuarios(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    """
    Lista usuarios con paginación.
    Ejemplo:
      /usuarios?limit=100&offset=0
    """
    usuarios = logica.listar_usuarios(db, limit=limit, offset=offset)

    salida: list[UsuarioAdminOut] = []
    for u in usuarios:
        roles = getattr(u, "roles", None) or []
        rol_nombre = roles[0].nombre if len(roles) > 0 else None

        salida.append(
            UsuarioAdminOut(
                usuario_id=str(u.usuario_id),
                targeta_id=str(u.targeta_id) if u.targeta_id else None,
                nombre=u.nombre,
                apellido=u.apellido,
                correo=u.correo,
                rol=rol_nombre,
            )
        )

    return salida


@router.post("/usuarios", response_model=UsuarioAdminOut, status_code=201)
def crear_usuario_admin(
    data: UsuarioAdminCreateIn,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    """Crea un usuario nuevo."""
    try:
        usuario = logica.crear_usuario_admin(
            db=db,
            nombre=data.nombre,
            apellido=data.apellido,
            correo=data.correo,
            targeta_id=data.targeta_id,
            rol=data.rol,
            contrasena=data.contrasena,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    roles = getattr(usuario, "roles", None) or []
    rol_nombre = roles[0].nombre if len(roles) > 0 else None

    return UsuarioAdminOut(
        usuario_id=str(usuario.usuario_id),
        targeta_id=str(usuario.targeta_id) if usuario.targeta_id else None,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        correo=usuario.correo,
        rol=rol_nombre,
    )


@router.put("/usuarios/{usuario_id}", response_model=UsuarioAdminOut)
def actualizar_usuario_admin(
    usuario_id: str,
    data: UsuarioAdminUpdateIn,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    """Actualiza los datos de un usuario (sin cambiar la contraseña)."""
    try:
        usuario = logica.actualizar_usuario_admin(
            db=db,
            usuario_id=usuario_id,
            nombre=data.nombre,
            apellido=data.apellido,
            correo=data.correo,
            targeta_id=data.targeta_id,
            rol=data.rol,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    roles = getattr(usuario, "roles", None) or []
    rol_nombre = roles[0].nombre if len(roles) > 0 else None

    return UsuarioAdminOut(
        usuario_id=str(usuario.usuario_id),
        targeta_id=str(usuario.targeta_id) if usuario.targeta_id else None,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        correo=usuario.correo,
        rol=rol_nombre,
    )


@router.delete("/usuarios/{usuario_id}", status_code=204)
def eliminar_usuario_admin(
    usuario_id: str,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    """Elimina un usuario."""
    try:
        logica.eliminar_usuario_admin(db=db, usuario_id=usuario_id)
    except ValueError as e:
        msg = str(e).lower()
        if "no encontrado" in msg:
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    return
