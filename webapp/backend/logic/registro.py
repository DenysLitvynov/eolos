"""
Autor: Denys Litvynov Lymanets
Fecha: 15-11-2025
Descripción: Lógica de negocio para el registro. Valida datos, maneja pendientes y verificación por email.
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
        
        # Validar correo único (en usuarios y pendientes)
        correo_existente = db.query(Usuario).filter(Usuario.correo == correo).first() or \
                           db.query(PendingRegistration).filter(PendingRegistration.correo == correo).first()
        if correo_existente:
            raise ValueError("Correo ya registrado o en proceso")
        
        return True
    
    # ---------------------------------------------------------

    def hashear_contrasena(self, contrasena: str):
        return pwd_context.hash(contrasena)

    # ---------------------------------------------------------

    def generar_codigo_verificacion(self):
        return f"{random.randint(100000, 999999)}"

    # ---------------------------------------------------------

    def enviar_email_verificacion(self, correo: str, codigo: str):
        try:
            msg = MIMEText(f"Tu código de verificación es: {codigo}. Expira en 15 minutos.")
            msg['Subject'] = "Código de Verificación para Registro"
            msg['From'] = FROM_EMAIL
            msg['To'] = correo

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(FROM_EMAIL, [correo], msg.as_string())
            return True
        except Exception as e:
            raise RuntimeError(f"Error enviando email: {e}")

    # ---------------------------------------------------------

    def iniciar_registro(self, db: Session, nombre: str, apellido: str, correo: str, targeta_id: str, contrasena: str, contrasena_repite: str, acepta_politica: bool):
        """
        Inicia el proceso de registro guardando en pending y enviando código.
        """
        try:
            self.validar_datos(db, nombre, apellido, correo, targeta_id, contrasena, contrasena_repite, acepta_politica)
            
            hash_contrasena = self.hashear_contrasena(contrasena)
            codigo = self.generar_codigo_verificacion()
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

            # Eliminar pendientes anteriores para este correo
            db.query(PendingRegistration).filter(PendingRegistration.correo == correo).delete()
            db.commit()

            pendiente = PendingRegistration(
                id=str(uuid.uuid4()),
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                targeta_id=targeta_id,
                contrasena_hash=hash_contrasena,
                verification_code=codigo,
                expires_at=expires_at
            )
            db.add(pendiente)
            db.commit()

            self.enviar_email_verificacion(correo, codigo)
            return True
        except ValueError as e:
            raise e
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error iniciando registro: {e}")

    # ---------------------------------------------------------

    def reenviar_codigo(self, db: Session, correo: str):
        """
        Reenvía un nuevo código de verificación, invalidando el anterior.
        """
        try:
            pendiente = db.query(PendingRegistration).filter(PendingRegistration.correo == correo).first()
            if not pendiente:
                raise ValueError("No hay registro pendiente para este correo")
            if pendiente.expires_at < datetime.now(timezone.utc):
                raise ValueError("Registro pendiente expirado, inicia de nuevo")

            codigo = self.generar_codigo_verificacion()
            pendiente.verification_code = codigo
            pendiente.expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
            db.commit()

            self.enviar_email_verificacion(correo, codigo)
            return True
        except ValueError as e:
            raise e
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error reenviando código: {e}")

    # ---------------------------------------------------------

    def verificar_y_completar(self, db: Session, correo: str, verification_code: str):
        """
        Verifica el código y completa el registro creando el usuario, con auto-login.
        """
        try:
            pendiente = db.query(PendingRegistration).filter(PendingRegistration.correo == correo).first()
            if not pendiente:
                raise ValueError("No hay registro pendiente para este correo")
            if pendiente.verification_code != verification_code:
                raise ValueError("Código de verificación incorrecto")
            if pendiente.expires_at < datetime.now(timezone.utc):
                raise ValueError("Código de verificación expirado")

            nuevo_usuario = Usuario(
                usuario_id=str(uuid.uuid4()),
                targeta_id=pendiente.targeta_id,
                nombre=pendiente.nombre,
                apellido=pendiente.apellido,
                correo=pendiente.correo,
                contrasena_hash=pendiente.contrasena_hash
            )
            
            # Asignar rol "usuario" por defecto
            rol_usuario = db.query(Rol).filter(Rol.nombre == "usuario").one_or_none()
            if not rol_usuario:
                raise RuntimeError("Rol 'usuario' no encontrado en la BD")
            nuevo_usuario.roles.append(rol_usuario)
            
            db.add(nuevo_usuario)
            db.delete(pendiente)
            db.commit()

            # Auto-login generando token
            logica_login = LogicaLogin()
            return logica_login.generar_token(nuevo_usuario)
        except ValueError as e:
            raise e
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error completando registro: {e}")

# ---------------------------------------------------------
