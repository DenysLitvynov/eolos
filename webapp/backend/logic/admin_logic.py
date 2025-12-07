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

from ..db.models import Usuario, Rol  # 如果还有 UsuarioRol 模型也可以引

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
        按 roles.nombre 查找角色，忽略大小写和前后空格
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
        # 如果在模型里 relationship roles 配了 lazy='joined'，这里直接 all 就行
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

        # 1) contraseña
        if not self._password_valida(contrasena):
            raise ValueError(
                "La contraseña no cumple los requisitos: mínimo 8 caracteres, "
                "incluyendo mayúsculas, minúsculas, números y símbolos (@$!%*?&)"
            )

        # 2) correo único
        correo = correo.strip().lower()
        existe = db.query(Usuario).filter(Usuario.correo == correo).first()
        if existe:
            raise ValueError("El correo ya está en uso por otro usuario")

        # 3) targeta_id normalizado
        if targeta_id is not None:
            targeta_id = str(targeta_id).strip()
            if targeta_id == "" or targeta_id.lower() == "null":
                targeta_id = None

        # 4) crear usuario
        usuario = Usuario(
            usuario_id=str(uuid4()),  # 如果模型里 default 已经是 uuid4，可以不传
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            correo=correo,
            targeta_id=targeta_id,
            contrasena_hash=pwd_context.hash(contrasena),
        )

        # 5) 关联角色（假设一个用户只有一个主角色）
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

        # correo único
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

        # 角色更新：清空旧的，只保留一个
        if rol is not None:
            nuevo_rol = self._obtener_rol_por_nombre(db, rol)
            usuario.roles.clear()
            usuario.roles.append(nuevo_rol)

        db.commit()
        db.refresh(usuario)
        return usuario

    def eliminar_usuario_admin(self, db: Session, usuario_id: str) -> None:
        """
        删除用户：
        - 先清空 usuario_roles (通过 relationship roles)
        - 再尝试删除 usuarios
        - 如果还有其它外键（trayectos, incidencias 等），捕获 IntegrityError，
          抛出友好的 ValueError，让 API 返回 400，而不是 500。
        """
        usuario = self._obtener_usuario(db, usuario_id)

        # 先清关系 (usuario_roles)
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
