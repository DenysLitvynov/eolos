"""
Autor: jinwei
Fecha: 07-12-2025
Descripción: Lógica de negocio para la administración de usuarios.
"""

from typing import List, Optional
from uuid import uuid4
import re

from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from ..db.models import Usuario, Rol  # Si existe un modelo UsuarioRol también podría importarse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LogicaAdmin:
    # ========= helpers internos =========

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

    def _obtener_usuario(self, db: Session, usuario_id: str) -> Usuario:
        usuario = (
            db.query(Usuario)
            .filter(Usuario.usuario_id == str(usuario_id))
            .first()
        )
        if not usuario:
            raise ValueError("Usuario no encontrado")
        return usuario

    def _obtener_rol_por_nombre(self, db: Session, nombre_rol: str) -> Rol:
        """
        Buscar rol según roles.nombre, ignorando mayúsculas/minúsculas y espacios.
        """
        nombre_rol = nombre_rol.strip()
        rol = (
            db.query(Rol)
            .filter(func.lower(Rol.nombre) == nombre_rol.lower())
            .first()
        )
        if not rol:
            raise ValueError(f"Rol '{nombre_rol}' no existe en la tabla roles")
        return rol

    # ========= API público =========

    def listar_usuarios(self, db: Session) -> List[Usuario]:
        # Si el modelo tiene relationship roles con lazy='joined', un simple all() basta
        return db.query(Usuario).order_by(Usuario.usuario_id).all()

    def crear_usuario_admin(
        self,
        db: Session,
        *,
        nombre: str,
        apellido: str,
        correo: str,
        targeta_id: Optional[str],
        rol: str,
        contrasena: str,
    ) -> Usuario:

        # 1) Validación de contraseña
        if not self._password_valida(contrasena):
            raise ValueError(
                "La contraseña no cumple los requisitos: mínimo 8 caracteres, "
                "incluyendo mayúsculas, minúsculas, números y símbolos (@$!%*?&)"
            )

        # 2) Correo único
        correo = correo.strip().lower()
        existe = db.query(Usuario).filter(Usuario.correo == correo).first()
        if existe:
            raise ValueError("El correo ya está en uso por otro usuario")

        # 3) Normalización de targeta_id
        if targeta_id is not None:
            targeta_id = str(targeta_id).strip()
            if targeta_id == "" or targeta_id.lower() == "null":
                targeta_id = None

        # 4) Crear usuario
        usuario = Usuario(
            usuario_id=str(uuid4()),  # Si el modelo ya tiene default=uuid4, este valor podría omitirse
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            correo=correo,
            targeta_id=targeta_id,
            contrasena_hash=pwd_context.hash(contrasena),
        )

        # 5) Asociar rol (suponiendo que un usuario solo tiene un rol principal)
        rol_obj = self._obtener_rol_por_nombre(db, rol)
        usuario.roles.append(rol_obj)

        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    def actualizar_usuario_admin(
        self,
        db: Session,
        *,
        usuario_id: str,
        nombre: Optional[str] = None,
        apellido: Optional[str] = None,
        correo: Optional[str] = None,
        targeta_id: Optional[str] = None,
        rol: Optional[str] = None,
    ) -> Usuario:
        usuario = self._obtener_usuario(db, usuario_id)

        # Validación y unicidad del correo
        if correo is not None:
            correo = correo.strip().lower()
            if correo != usuario.correo:
                existe = (
                    db.query(Usuario)
                    .filter(Usuario.correo == correo)
                    .first()
                )
                if existe:
                    raise ValueError("El correo ya está en uso por otro usuario")
                usuario.correo = correo

        if nombre is not None:
            usuario.nombre = nombre.strip()
        if apellido is not None:
            usuario.apellido = apellido.strip()

        if targeta_id is not None:
            targeta_id = str(targeta_id).strip()
            usuario.targeta_id = (
                None if targeta_id == "" or targeta_id.lower() == "null" else targeta_id
            )

        # Actualización del rol: limpiar rol anterior y asignar uno nuevo
        if rol is not None:
            nuevo_rol = self._obtener_rol_por_nombre(db, rol)
            usuario.roles.clear()
            usuario.roles.append(nuevo_rol)

        db.commit()
        db.refresh(usuario)
        return usuario

    def eliminar_usuario_admin(self, db: Session, usuario_id: str) -> None:
        """
        Eliminación de usuario:
        - Primero limpiar usuario_roles (mediante la relación roles)
        - Luego intentar borrar el usuario
        - Si existen otras claves foráneas (trayectos, incidencias, etc.),
          capturar IntegrityError y lanzar un ValueError más amigable,
          para que la API devuelva 400 en lugar de 500.
        """
        usuario = self._obtener_usuario(db, usuario_id)

        # Limpiar relaciones (usuario_roles)
        usuario.roles.clear()

        try:
            db.delete(usuario)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError(
                "No se puede eliminar el usuario porque tiene datos relacionados "
                "(por ejemplo trayectos, incidencias, etc.)"
            )
