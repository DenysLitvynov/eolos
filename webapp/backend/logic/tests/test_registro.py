"""
Autor: Denys Litvynov Lymanets
Fecha: 27-10-2025
Descripción: Tests para LogicaRegistro usando BD temporal en memoria.
"""

# ---------------------------------------------------------

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...db.models import Base, Usuario, Mibisivalencia, Rol
from ..registro import LogicaRegistro
from passlib.context import CryptContext
import uuid

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
        rol_id=1,
        nombre="Usuario",
        apellido="Prueba1",
        correo="prueba1@fake.com",
        contrasena_hash=hash1
    )
    hash2 = pwd_context.hash("password2")
    usuario2 = Usuario(
        usuario_id=str(uuid.uuid4()),
        targeta_id=None,
        rol_id=2,
        nombre="Admin",
        apellido="Prueba2",
        correo="prueba2@fake.com",
        contrasena_hash=hash2
    )
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
    carnet = db_session.query(Mibisivalencia).filter(Mibisivalencia.targeta_id == "87654321B").first()
    assert logica.validar_datos(db_session, "Test", "User", "test@fake.com", "87654321B", "pass12345", "pass12345") is True

# ---------------------------------------------------------

def test_validar_datos_contrasenas_no_coinciden(db_session):
    logica = LogicaRegistro()
    carnet = db_session.query(Mibisivalencia).filter(Mibisivalencia.targeta_id == "87654321B").first()
    with pytest.raises(ValueError):
        logica.validar_datos(db_session, "Test", "User", "test@fake.com", "87654321B", "pass12345", "wrong")

# ---------------------------------------------------------

def test_validar_datos_targeta_no_existe(db_session):
    logica = LogicaRegistro()
    with pytest.raises(ValueError):
        logica.validar_datos(db_session, "Test", "User", "test@fake.com", "99999999X", "pass12345", "pass12345")

# ---------------------------------------------------------

def test_validar_datos_targeta_ya_usada(db_session):
    logica = LogicaRegistro()
    # Usar carnet ya asociado (12345678A usado por usuario1)
    carnet_usado = db_session.query(Mibisivalencia).filter(Mibisivalencia.targeta_id == "12345678A").first()
    with pytest.raises(ValueError):
        logica.validar_datos(db_session, "Test", "User", "test@fake.com", "12345678A", "pass12345", "pass12345")

# ---------------------------------------------------------

def test_registrar_exitoso(db_session):
    logica = LogicaRegistro()
    carnet = db_session.query(Mibisivalencia).filter(Mibisivalencia.targeta_id == "87654321B").first()
    exito = logica.registrar(db_session, "Nuevo", "Usuario", "nuevo@fake.com", "87654321B", "pass12345", "pass12345")
    assert exito is True
    
    usuario = db_session.query(Usuario).filter(Usuario.correo == "nuevo@fake.com").first()
    assert usuario is not None
    assert usuario.targeta_id == "87654321B"

# ---------------------------------------------------------

def test_registrar_fallido_correo_duplicado(db_session):
    logica = LogicaRegistro()
    carnet = db_session.query(Mibisivalencia).filter(Mibisivalencia.targeta_id == "87654321B").first()
    logica.registrar(db_session, "Nuevo", "Usuario", "nuevo@fake.com", "87654321B", "pass12345", "pass12345")
    
    with pytest.raises(ValueError):
        logica.registrar(db_session, "Otro", "Usuario", "nuevo@fake.com", "87654321B", "pass12345", "pass12345")

# ---------------------------------------------------------
