"""
Autor: Denys Litvynov Lymanets
Fecha: 27-10-2025
Descripción: Lógica de negocio para el registro. Valida datos y inserta usuario.
"""

# ---------------------------------------------------------

from sqlalchemy.orm import Session
from ..db.models import Usuario, Mibisivalencia
from passlib.context import CryptContext
import uuid
import re

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
            targeta_id (str): ID de targeta.
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
        
        # Validar targeta_id existe en mibisivalencia
        existe_targeta = db.query(Mibisivalencia).filter(Mibisivalencia.targeta_id == uuid.UUID(targeta_id)).first()
        if not existe_targeta:
            raise ValueError("ID de targeta no existe en el sistema de bicis")
        
        # Validar targeta_id NO usado en usuarios
        usuario_existente = db.query(Usuario).filter(Usuario.targeta_id == uuid.UUID(targeta_id)).first()
        if usuario_existente:
            raise ValueError("ID de targeta ya registrado por otro usuario")
        
        # Validar correo único
        correo_existente = db.query(Usuario).filter(Usuario.correo == correo).first()
        if correo_existente:
            raise ValueError("Correo ya registrado")
        
        return True
