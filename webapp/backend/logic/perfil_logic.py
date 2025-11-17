"""
Autor: JINWEI
Fecha: 5-11-2025
Descripción: Lógica de negocio del perfil de usuario (tabla 'usuarios').
"""

from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..db.models import Usuario

# Contexto usado para encriptar contraseñas mediante bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LogicaPerfil:
    def obtener_perfil(self, db: Session, usuario_id: str) -> Usuario:
        """
        Obtiene el perfil de un usuario por su ID.
        Lanza ValueError si el usuario no existe.
        """
        usuario = db.query(Usuario).filter(Usuario.usuario_id == str(usuario_id)).first()
        if not usuario:
            raise ValueError("Usuario no encontrado")
        return usuario

    def actualizar_perfil(
        self,
        db: Session,
        usuario_id: str,
        *,
        nombre: Optional[str] = None,
        apellido: Optional[str] = None,
        correo: Optional[str] = None,
        targeta_id: Optional[str] = None,
        contrasena: Optional[str] = None,
    ) -> Usuario:
        """
        Actualiza la información del perfil de un usuario.

        Campos que se pueden modificar:
          - nombre, apellido, correo, targeta_id, contrasena.
        """
        usuario = self.obtener_perfil(db, usuario_id)

        # Normalización de cadenas para evitar espacios y errores comunes
        if nombre is not None:
            nombre = nombre.strip()
        if apellido is not None:
            apellido = apellido.strip()
        if correo is not None:
            correo = correo.strip().lower()   # Es habitual almacenar correos en minúsculas
        if targeta_id is not None:
            targeta_id = targeta_id.strip()

        # Validar que el correo nuevo no esté siendo usado por otro usuario
        if correo is not None and correo != usuario.correo:
            existe = db.query(Usuario).filter(Usuario.correo == correo).first()
            if existe:
                raise ValueError("El correo ya está en uso por otro usuario")
            usuario.correo = correo

        # Actualizar atributos básicos
        if nombre is not None:
            usuario.nombre = nombre

        # Campo opcional 'apellido': lo mantienes por compatibilidad con el frontend
        if apellido is not None:
            usuario.apellido = apellido

        # targeta_id: convertir "" o "null" en valor NULL en la BD
        if targeta_id is not None:
            if targeta_id == "" or targeta_id.lower() == "null":
                usuario.targeta_id = None
            else:
                usuario.targeta_id = targeta_id  # El validador Pydantic controla longitud máx.

        # Actualizar contraseña solo si se proporciona
        if contrasena:
            usuario.contrasena_hash = pwd_context.hash(contrasena)

        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario
