"""
Autor: JINWEI
Fecha: 5-11-2025
Descripción: Lógica de negocio segura del perfil de usuario.
"""

from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import re

from ..db.models import Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LogicaPerfil:
    def obtener_perfil(self, db: Session, usuario_id: str) -> Usuario:
        usuario = (
            db.query(Usuario)
            .filter(Usuario.usuario_id == str(usuario_id))
            .first()
        )
        if not usuario:
            raise ValueError("Usuario no encontrado")
        return usuario

    def _password_valida(self, password: str) -> bool:
        """
        Reglas iguales al registro:
            - Mínimo 8 caracteres
            - Mayúsculas
            - Minúsculas
            - Números
            - Símbolos especiales
        """
        patron = re.compile(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
        )
        return bool(patron.match(password))

    def actualizar_perfil(
        self,
        db: Session,
        usuario_id: str,
        *,
        nombre: Optional[str] = None,
        apellido: Optional[str] = None,
        correo: Optional[str] = None,
        targeta_id: Optional[str] = None,
        contrasena_actual: Optional[str] = None,
        contrasena_nueva: Optional[str] = None,
    ) -> Usuario:
        usuario = self.obtener_perfil(db, usuario_id)

        # ====== 1) Validar contraseña actual (obligatoria para cualquier cambio)
        if not contrasena_actual:
            raise ValueError("Debes introducir tu contraseña actual")

        if not pwd_context.verify(contrasena_actual, usuario.contrasena_hash):
            raise ValueError("La contraseña actual no es correcta")

        # ====== 2) Validación de correo único
        if correo is not None:
            correo = correo.strip().lower()
            if correo != usuario.correo:
                existe = (
                    db.query(Usuario)
                    .filter(Usuario.correo == correo)
                    .first()
                )
                if existe:
                    raise ValueError(
                        "El correo ya está en uso por otro usuario"
                    )
                usuario.correo = correo

        # ====== 3) Actualizar campos simples
        if nombre is not None:
            usuario.nombre = nombre.strip()

        if apellido is not None:
            usuario.apellido = apellido.strip()

        # targeta_id: "" → None
        if targeta_id is not None:
            targeta_id = str(targeta_id).strip()
            usuario.targeta_id = (
                None if targeta_id == "" or targeta_id.lower() == "null" else targeta_id
            )


        # ====== 5) Si hay contraseña nueva → validar reglas & actualizar hash
        if contrasena_nueva:
            if not self._password_valida(contrasena_nueva):
                raise ValueError(
                    "La nueva contraseña no cumple los requisitos: mínimo 8 caracteres, "
                    "incluyendo mayúsculas, minúsculas, números y símbolos (@$!%*?&)"
                )

            usuario.contrasena_hash = pwd_context.hash(contrasena_nueva)

        db.commit()
        db.refresh(usuario)
        return usuario
