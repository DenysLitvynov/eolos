"""
Autor: Denys Litvynov Lymanets
Fecha: 26-10-2025
Descripción: Tests para LogicaLogin usando BD temporal con SQLAlchemy.
"""

# ---------------------------------------------------------

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...db.models import Base, Usuario, Rol
from ..login import LogicaLogin
from passlib.context import CryptContext
import uuid

# ---------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")  # BD temporal en memoria
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Insertar rol de prueba
    test_rol = Rol(
        rol_id=1,
        nombre="usuario",
        descripcion="Usuario estándar"
    )
    session.add(test_rol)
    session.commit()  # Commit para que el rol exista antes de asignar
    
    # Insertar datos de prueba directamente
    hash_test = pwd_context.hash("Testpass123!")
    test_user = Usuario(
        usuario_id=str(uuid.uuid4()),
        nombre="Test",
        apellido="User",
        correo="test@fake.com",
        contrasena_hash=hash_test
    )
    test_user.roles.append(test_rol)  # Asignar rol via relación
    session.add(test_user)
    session.commit()
    
    yield session
    Base.metadata.drop_all(engine)

# ---------------------------------------------------------

def test_validar_credenciales_correctas(db_session):
    logica = LogicaLogin()
    usuario = logica.validar_credenciales(db_session, "test@fake.com", "Testpass123!")
    assert usuario is not None
    assert usuario.correo == "test@fake.com"

# ---------------------------------------------------------

def test_validar_credenciales_incorrectas(db_session):
    logica = LogicaLogin()
    usuario = logica.validar_credenciales(db_session, "test@fake.com", "wrongpass")
    assert usuario is None

# ---------------------------------------------------------

def test_generar_token(db_session):
    logica = LogicaLogin()
    usuario = db_session.query(Usuario).first()  # Usa el usuario creado en fixture
    token = logica.generar_token(usuario)
    assert isinstance(token, str)
    assert len(token) > 0

# ---------------------------------------------------------

def test_login_exitoso(db_session):
    logica = LogicaLogin()
    token = logica.login(db_session, "test@fake.com", "Testpass123!")
    assert isinstance(token, str)

# ---------------------------------------------------------

def test_login_fallido(db_session):
    logica = LogicaLogin()
    with pytest.raises(ValueError):
        logica.login(db_session, "test@fake.com", "wrongpass")

# ---------------------------------------------------------
