"""
Autor: Denys Litvynov Lymanets
Fecha: 26-10-2025
Descripción: Lógica de negocio para el login. Valida credenciales y genera JWT.
"""

# ---------------------------------------------------------

from sqlalchemy.orm import Session
from ..db.models import Usuario
from passlib.context import CryptContext
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ---------------------------------------------------------

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------

class LogicaLogin:

    def validar_credenciales(self, db: Session, correo: str, contrasena: str):
        """
        Valida las credenciales del usuario.
        
        Args:
            db (Session): Sesión de BD.
            correo (str): Correo del usuario.
            contrasena (str): Contraseña plana.
        
        Returns:
            Usuario: Objeto usuario si válido, None si no.
        """
        try:
            usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
            if usuario and pwd_context.verify(contrasena, usuario.contrasena_hash):
                return usuario
            return None
        except Exception as e:
            raise RuntimeError(f"Error validando credenciales: {e}")

    # ---------------------------------------------------------

    # ---------------------------------------------------------

    # ---------------------------------------------------------

    # ---------------------------------------------------------
