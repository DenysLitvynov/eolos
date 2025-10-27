"""
Autor: Denys Litvynov Lymanets
Fecha: 26-10-2025
Descripción: Rutas para autenticación 
"""

# ---------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..logic.login import LogicaLogin
from ..logic.registro import LogicaRegistro
from ..db.database import get_db
from sqlalchemy.orm import Session

# ---------------------------------------------------------

router = APIRouter(prefix="/auth")

class LoginRequest(BaseModel):
    correo: str
    contrasena: str

class RegistroRequest(BaseModel):
    nombre: str
    apellido: str
    correo: str
    targeta_id: str
    contrasena: str
    contrasena_repite: str

class ResponseToken(BaseModel):
    token: str

class ResponseRegistro(BaseModel):
    exito: bool
    mensaje: str

# ---------------------------------------------------------

@router.post("/login")
def ruta_login(login_data: LoginRequest, db: Session = Depends(get_db)):
    try:
        logica = LogicaLogin()
        token = logica.login(db, login_data.correo, login_data.contrasena)
        return ResponseToken(token=token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------

@router.post("/registro")
def ruta_registro(registro_data: RegistroRequest, db: Session = Depends(get_db)):
    try:
        logica = LogicaRegistro()
        exito = logica.registrar(
            db,
            registro_data.nombre,
            registro_data.apellido,
            registro_data.correo,
            registro_data.targeta_id,
            registro_data.contrasena,
            registro_data.contrasena_repite
        )
        return ResponseRegistro(exito=exito, mensaje="Registro exitoso")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------
