"""
Autor: JINWEI
Fecha: 5-11-2025
Descripción: Lógica de negocio del perfil de usuario (tabla 'usuarios').
"""

from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..db.models import Usuario

# Contexto para encriptar contraseñas con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LogicaPerfil:
    def obtener_perfil(self, db: Session, usuario_id: str) -> Usuario:
        """
        Obtiene el perfil de un usuario a partir de su ID.

        Parámetros:
            db (Session): Sesión de base de datos de SQLAlchemy.
            usuario_id (str): ID único del usuario.

        Retorna:
            Usuario: Objeto del modelo Usuario correspondiente.

        Lanza:
            ValueError: Si el usuario no existe.
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

        Parámetros:
            db (Session): Sesión de base de datos.
            usuario_id (str): ID del usuario autenticado.
            nombre (str, opcional): Nuevo nombre.
            apellido (str, opcional): Nuevo apellido.
            correo (str, opcional): Nuevo correo (verifica duplicados).
            targeta_id (str, opcional): Nuevo ID de la tarjeta asociada.
            contrasena (str, opcional): Nueva contraseña (se encripta si se proporciona).

        Retorna:
            Usuario: Objeto Usuario actualizado.

        Lanza:
            ValueError: Si el usuario no existe o el correo ya está en uso.
        """
        usuario = self.obtener_perfil(db, usuario_id)

        # Validar si el nuevo correo está en uso por otro usuario
        if correo is not None and correo != usuario.correo:
            existe = db.query(Usuario).filter(Usuario.correo == correo).first()
            if existe:
                raise ValueError("El correo ya está en uso por otro usuario")
            usuario.correo = correo

        # Actualizar los campos si se proporcionan
        if nombre is not None:
            usuario.nombre = nombre
        if apellido is not None:
            usuario.apellido = apellido
        if targeta_id is not None:
            usuario.targeta_id = targeta_id
        if contrasena:
            usuario.contrasena_hash = pwd_context.hash(contrasena)

        # Guardar los cambios en la base de datos
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario
