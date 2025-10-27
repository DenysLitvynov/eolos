"""
Autor: Denys Litvynov Lymanets
Fecha: 27-10-2025
Descripción: Lógica de negocio para el registro. Valida datos y inserta usuario.
"""

# ---------------------------------------------------------

from sqlalchemy.orm import Session
from ..db.models import Usuario, Mibisivalencia
from passlib.context import CryptContext
import re
import uuid  # Añadido para generar UUID en usuario_id

# ---------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------

class LogicaRegistro:
    
    def validar_datos(self, db: Session, nombre: str, apellido: str, correo: str, targeta_id: str, contrasena: str, contrasena_repite: str):
        """
        Valida los datos de registro.
        
        Args:
            db (Session): Sesión de BD.
            nombre (str): Nombre.
            apellido (str): Apellido.
            correo (str): Correo.
            targeta_id (str): ID de carnet (formato DNI: 8 dígitos + letra).
            contrasena (str): Contraseña.
            contrasena_repite (str): Repetición de contraseña.
        
        Returns:
            bool: True si válido.
        """
        if contrasena != contrasena_repite:
            raise ValueError("Las contraseñas no coinciden")
        
        if len(contrasena) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            raise ValueError("Correo inválido")
        
        # Validar formato DNI (8 dígitos + 1 letra mayúscula)
        if not re.match(r"^\d{8}[A-Z]$", targeta_id):
            raise ValueError("ID de carnet inválido, debe ser 8 dígitos seguidos de una letra mayúscula")
        
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
        """
        Hashea la contraseña.
        
        Args:
            contrasena (str): Contraseña plana.
        
        Returns:
            str: Hash.
        """
        return pwd_context.hash(contrasena.encode("utf-8")[:72])
    
    # ---------------------------------------------------------
    
    def registrar(self, db: Session, nombre: str, apellido: str, correo: str, targeta_id: str, contrasena: str, contrasena_repite: str):
        """
        Proceso completo de registro.
        
        Args:
            ... (como en validar_datos)
        
        Returns:
            bool: True si éxito.
        """
        try:
            self.validar_datos(db, nombre, apellido, correo, targeta_id, contrasena, contrasena_repite)
            hash_contrasena = self.hashear_contrasena(contrasena)
            nuevo_usuario = Usuario(
                usuario_id=str(uuid.uuid4()),
                targeta_id=targeta_id,
                rol_id=1,  # Default: usuario
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                contrasena_hash=hash_contrasena
            )
            db.add(nuevo_usuario)
            db.commit()
            return True
        except ValueError as e:
            raise e
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error registrando usuario: {e}")

# ---------------------------------------------------------
