"""
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Lógica de negocio para recuperación de contraseña.
"""

# ---------------------------------------------------------

from sqlalchemy.orm import Session
from ..db.models import Usuario, PasswordResetToken
from passlib.context import CryptContext
import uuid
from datetime import datetime, timedelta, UTC, timezone
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import re

# ---------------------------------------------------------

load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Regex contraseña fuerte (mínimo 8, mayús, minús, número y símbolo)
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)

# ---------------------------------------------------------

class LogicaResetPassword:

    def enviar_reset_token(self, db: Session, correo: str):
        """
        Envía un token de reset al correo del usuario, invalidando anteriores.
        """
        try:
            usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
            if not usuario:
                raise ValueError("Correo no registrado")  # Genérico

            token = str(uuid.uuid4())
            expires_at = datetime.now(UTC) + timedelta(minutes=15)

            # Eliminar tokens anteriores para este usuario
            db.query(PasswordResetToken).filter(PasswordResetToken.usuario_id == usuario.usuario_id).delete()
            db.commit()

            reset_token = PasswordResetToken(
                id=str(uuid.uuid4()),
                usuario_id=usuario.usuario_id,
                token=token,
                expires_at=expires_at
            )
            db.add(reset_token)
            db.commit()

            enlace = f"{BASE_URL}/pages/reset-password.html?token={token}"
            msg = MIMEText(f"Para resetear tu contraseña, haz clic aquí: {enlace}. Expira en 15 minutos.")
            msg['Subject'] = "Recuperación de Contraseña"
            msg['From'] = FROM_EMAIL
            msg['To'] = correo

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(FROM_EMAIL, [correo], msg.as_string())

            return True
        except ValueError as e:
            raise e
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error enviando token de reset: {e}")

    def resetear_contrasena(self, db: Session, token: str, contrasena: str, contrasena_repite: str):
        """
        Resetea la contraseña usando el token, validando seguridad.
        """
        try:
            reset_token = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
            if not reset_token:
                raise ValueError("Token inválido o expirado")
            if reset_token.used:
                raise ValueError("Token ya usado")
            # Asegurarse de que expires_at tenga zona horaria
            expires_at = reset_token.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=UTC)
            if expires_at < datetime.now(UTC):
                raise ValueError("Token expirado")

            if contrasena != contrasena_repite:
                raise ValueError("Las contraseñas no coinciden")
            
            if not PASSWORD_REGEX.match(contrasena):
                raise ValueError("La contraseña debe tener mínimo 8 caracteres, mayúscula, minúscula, número y símbolo")

            usuario = db.query(Usuario).filter(Usuario.usuario_id == reset_token.usuario_id).first()
            if not usuario:
                raise ValueError("Usuario no encontrado")

            usuario.contrasena_hash = pwd_context.hash(contrasena)
            reset_token.used = True
            db.commit()

            return True
        except ValueError as e:
            raise e
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error reseteando contraseña: {e}")

# ---------------------------------------------------------
