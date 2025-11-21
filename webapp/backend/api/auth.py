"""
Autor: Denys Litvynov Lymanets
Fecha: 15-11-2025
Descripción: Rutas del servidor para las funcionalidades de autenticación (registro, login, otros) 
"""

# ---------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..logic.login import LogicaLogin
from ..logic.registro import LogicaRegistro
from ..logic.reset_password import LogicaResetPassword
from ..db.database import get_db
from sqlalchemy.orm import Session

# ---------------------------------------------------------

router = APIRouter(prefix="/auth")

# Clases para represenetar los campos que tien que recibir la api o responder

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
    acepta_politica: bool = False   

class VerifyRegistrationRequest(BaseModel):
    correo: str
    verification_code: str

class ResendVerificationRequest(BaseModel):
    correo: str

class ForgotPasswordRequest(BaseModel):
    correo: str

class ResetPasswordRequest(BaseModel):
    token: str
    contrasena: str
    contrasena_repite: str

class ResponseToken(BaseModel):
    token: str

class Response(BaseModel):
    exito: bool
    mensaje: str

# ---------------------------------------------------------

@router.post("/login")
def ruta_login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Ruta para login de usuario
    """
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
    """
    Ruta para iniciar registro (envia codigo por email)
    """
    try:
        logica = LogicaRegistro()
        exito = logica.iniciar_registro(
            db,
            registro_data.nombre,
            registro_data.apellido,
            registro_data.correo,
            registro_data.targeta_id,
            registro_data.contrasena,
            registro_data.contrasena_repite,
            registro_data.acepta_politica
        )
        return Response(exito=exito, mensaje="Código de verificación enviado al correo")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------

@router.post("/verify-registration")
def ruta_verify_registration(verify_data: VerifyRegistrationRequest, db: Session = Depends(get_db)):
    """
    Ruta para verificar código y completar el registro
    """
    try:
        logica = LogicaRegistro()
        token = logica.verificar_y_completar(db, verify_data.correo, verify_data.verification_code)
        return ResponseToken(token=token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------

@router.post("/resend-verification")
def ruta_resend_verification(resend_data: ResendVerificationRequest, db: Session = Depends(get_db)):
    """
    Ruta para reenviar el código de verificación para el registro
    """
    try:
        logica = LogicaRegistro()
        exito = logica.reenviar_codigo(db, resend_data.correo)
        return Response(exito=exito, mensaje="Código reenviado al correo")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------

@router.post("/forgot-password")
def ruta_forgot_password(forgot_data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Ruta para solicitar cambio de contraseña
    """
    try:
        logica = LogicaResetPassword()
        exito = logica.enviar_reset_token(db, forgot_data.correo)
        return Response(exito=exito, mensaje="Enlace de recuperación enviado al correo")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------

@router.post("/resend-reset")
def ruta_resend_reset(resend_data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Ruta para enviar token de reset
    """
    try:
        logica = LogicaResetPassword()
        exito = logica.enviar_reset_token(db, resend_data.correo)  
        return Response(exito=exito, mensaje="Enlace reenviado al correo")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------

@router.post("/reset-password")
def ruta_reset_password(reset_data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Ruta para resetear la contraseña con token
    """
    try:
        logica = LogicaResetPassword()
        exito = logica.resetear_contrasena(db, reset_data.token, reset_data.contrasena, reset_data.contrasena_repite)
        return Response(exito=exito, mensaje="Contraseña actualizada exitosamente")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------
