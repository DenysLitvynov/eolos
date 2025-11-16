"""
Autor: Denys Litvynov Lymanets
Fecha: 27-10-2025
Descripción: Tests para LogicaRegistro usando BD temporal en memoria.
"""

# ---------------------------------------------------------

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...db.models import Base, Usuario, Mibisivalencia, Rol, PendingRegistration
from ..registro import LogicaRegistro
from passlib.context import CryptContext
import uuid
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")  # BD temporal en memoria
    Base.metadata.create_all(engine)  # Crear tablas
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Insertar datos de prueba (seeds similares a seed.py)
    # Roles
    rol_usuario = Rol(rol_id=1, nombre="usuario", descripcion="Usuario estándar")
    rol_admin = Rol(rol_id=2, nombre="admin", descripcion="Administrador")
    session.add(rol_usuario)
    session.add(rol_admin)
    
    # Mibisivalencias (carnets)
    carnet1 = Mibisivalencia(targeta_id="12345678A")
    carnet2 = Mibisivalencia(targeta_id="87654321B")
    session.add(carnet1)
    session.add(carnet2)
    
    # Usuarios
    hash1 = pwd_context.hash("password1")
    usuario1 = Usuario(
        usuario_id=str(uuid.uuid4()),
        targeta_id="12345678A",
        nombre="Usuario",
        apellido="Prueba1",
        correo="prueba1@fake.com",
        contrasena_hash=hash1
    )
    usuario1.roles.append(rol_usuario)  # Asignar rol
    hash2 = pwd_context.hash("password2")
    usuario2 = Usuario(
        usuario_id=str(uuid.uuid4()),
        targeta_id=None,
        nombre="Admin",
        apellido="Prueba2",
        correo="prueba2@fake.com",
        contrasena_hash=hash2
    )
    usuario2.roles.append(rol_admin)
    session.add(usuario1)
    session.add(usuario2)
    
    session.commit()
    
    yield session
    session.close()
    Base.metadata.drop_all(engine)  # Limpieza

# ---------------------------------------------------------

def test_validar_datos_correctos(db_session):
    logica = LogicaRegistro()
    # Usar carnet no usado del fixture (carnet2: 87654321B)
    assert logica.validar_datos(db_session, "Test", "User", "test@fake.com", "87654321B", "Pass123!", "Pass123!", True) is True

# ---------------------------------------------------------

def test_validar_datos_contrasenas_no_coinciden(db_session):
    logica = LogicaRegistro()
    with pytest.raises(ValueError, match="Las contraseñas no coinciden"):
        logica.validar_datos(db_session, "Test", "User", "test@fake.com", "87654321B", "Pass123!", "wrong", True)

# ---------------------------------------------------------

def test_validar_datos_contrasena_debil(db_session):
    logica = LogicaRegistro()
    with pytest.raises(ValueError, match="La contraseña debe tener mínimo 8 caracteres"):
        logica.validar_datos(db_session, "Test", "User", "test@fake.com", "87654321B", "weakpass", "weakpass", True)

# ---------------------------------------------------------

def test_validar_datos_correo_invalido(db_session):
    logica = LogicaRegistro()
    with pytest.raises(ValueError, match="Correo inválido"):
        logica.validar_datos(db_session, "Test", "User", "invalid_email", "87654321B", "Pass123!", "Pass123!", True)

# ---------------------------------------------------------

def test_validar_datos_targeta_no_existe(db_session):
    logica = LogicaRegistro()
    with pytest.raises(ValueError, match="ID de carnet no existe"):
        logica.validar_datos(db_session, "Test", "User", "test@fake.com", "99999999X", "Pass123!", "Pass123!", True)

# ---------------------------------------------------------

def test_validar_datos_targeta_ya_usada(db_session):
    logica = LogicaRegistro()
    # Usar carnet ya asociado (12345678A usado por usuario1)
    with pytest.raises(ValueError, match="ID de carnet ya registrado"):
        logica.validar_datos(db_session, "Test", "User", "test@fake.com", "12345678A", "Pass123!", "Pass123!", True)

# ---------------------------------------------------------

def test_validar_datos_correo_duplicado(db_session):
    logica = LogicaRegistro()
    with pytest.raises(ValueError, match="Correo ya registrado"):
        logica.validar_datos(db_session, "Test", "User", "prueba1@fake.com", "87654321B", "Pass123!", "Pass123!", True)

# ---------------------------------------------------------

def test_validar_datos_acepta_politica_falso(db_session):
    logica = LogicaRegistro()
    with pytest.raises(ValueError, match="Debes aceptar la política"):
        logica.validar_datos(db_session, "Test", "User", "test@fake.com", "87654321B", "Pass123!", "Pass123!", False)

# ---------------------------------------------------------
