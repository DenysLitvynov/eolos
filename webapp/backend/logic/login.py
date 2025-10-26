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
from datetime import datetime, timedelta, timezone
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

    def generar_token(self, usuario_id: str, rol_id: int):
        """
        Genera un token JWT.
        
        Args:
            usuario_id (str): ID del usuario.
            rol_id (int): ID del rol.
        
        Returns:
            str: Token JWT.
        """
        try:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode = {"sub": str(usuario_id), "rol": rol_id, "exp": expire}
            return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        except Exception as e:
            raise RuntimeError(f"Error generando token: {e}")

    # ---------------------------------------------------------

    def login(self, db: Session, correo: str, contrasena: str):
        """
        Proceso completo de login.
        
        Args:
            db (Session): Sesión de BD.
            correo (str): Correo.
            contrasena (str): Contraseña.
        
        Returns:
            str: Token si éxito.
        """
        usuario = self.validar_credenciales(db, correo, contrasena)
        if not usuario:
            raise ValueError("Credenciales inválidas")
        return self.generar_token(str(usuario.usuario_id), usuario.rol_id)

# ---------------------------------------------------------
# class

