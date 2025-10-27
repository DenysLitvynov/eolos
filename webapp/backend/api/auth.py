"""
Autor: Denys Litvynov Lymanets
Fecha: 26-10-2025
Descripción: Rutas para autenticación 
"""

# ---------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..logic.login import LogicaLogin
from ..db.database import get_db
from sqlalchemy.orm import Session

# ---------------------------------------------------------

router = APIRouter(prefix="/auth")

class LoginRequest(BaseModel):
    correo: str
    contrasena: str

class ResponseToken(BaseModel):
    token: str

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
