"""
Autor: Denys Litvynov Lymanets
Fecha: 15-11-2025
Descripción: Lógica de negocio para el registro. Valida datos y inserta usuario.
"""

# ---------------------------------------------------------

from sqlalchemy.orm import Session
from ..db.models import Usuario, Mibisivalencia, Rol, PendingRegistration
from passlib.context import CryptContext
import re
import uuid
from datetime import datetime, timedelta, timezone
import random
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from .login import LogicaLogin

# ---------------------------------------------------------

load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Regex contraseña fuerte (mínimo 8, mayús, minús, número y símbolo)
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)

# ---------------------------------------------------------

class LogicaRegistro:

     def validar_datos(self, db: Session, nombre: str, apellido: str, correo: str, targeta_id: str, contrasena: str, contrasena_repite: str, acepta_politica: bool = False):
        """
        Valida los datos de registro.
        """
        if not acepta_politica:
            raise ValueError("Debes aceptar la política de privacidad y términos")
            
        if contrasena != contrasena_repite:
            raise ValueError("Las contraseñas no coinciden")
        
        if not PASSWORD_REGEX.match(contrasena):
            raise ValueError("La contraseña debe tener mínimo 8 caracteres, mayúscula, minúscula, número y símbolo")
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            raise ValueError("Correo inválido")
       
        if not re.match(r"^\d{8}[A-Z]$", targeta_id):
            raise ValueError("ID de carnet inválido: debe ser 8 dígitos + 1 letra mayúscula")
        
        # Validar targeta_id existe en mibisivalencia
        carnet = db.query(Mibisivalencia).filter(Mibisivalencia.targeta_id == targeta_id).first()
        if not carnet:
            raise ValueError("ID de carnet no existe en el sistema")
        
        # Validar targeta_id NO usado en usuarios
        usuario_existente = db.query(Usuario).filter(Usuario.targeta_id == targeta_id).first()
        if usuario_existente:
            raise ValueError("ID de carnet ya registrado por otro usuario")
        
        # Validar correo único
        correo_existente = db.query(Usuario).filter(Usuario.correo == correo).first()
        if correo_existente:
            raise ValueError("Correo ya registrado")
        
        return True
    
    # ---------------------------------------------------------

    def hashear_contrasena(self, contrasena: str):
        return pwd_context.hash(contrasena)

    # ---------------------------------------------------------

    def generar_codigo_verificacion(self):
        return f"{random.randint(100000, 999999)}"

    # ---------------------------------------------------------
    
    def registrar(self, db: Session, nombre: str, apellido: str, correo: str, targeta_id: str, contrasena: str, contrasena_repite: str, acepta_politica: bool):
        """
        Proceso completo de registro (temporal hasta que añadamos verificación por email).
        """
        try:
            self.validar_datos(db, nombre, apellido, correo, targeta_id, contrasena, contrasena_repite, acepta_politica)
            
            hash_contrasena = self.hashear_contrasena(contrasena)
            
            nuevo_usuario = Usuario(
                usuario_id=str(uuid.uuid4()),
                targeta_id=targeta_id,
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                contrasena_hash=hash_contrasena
            )
            
            # Asignar rol "usuario" por defecto
            rol_usuario = db.query(Rol).filter(Rol.nombre == "usuario").one_or_none()
            if not rol_usuario:
                raise RuntimeError("Rol 'usuario' no encontrado en la BD")
            nuevo_usuario.roles.append(rol_usuario)
            
            db.add(nuevo_usuario)
            db.commit()
            return True
        except ValueError as e:
            raise e
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error registrando usuario: {e}")

# ---------------------------------------------------------
