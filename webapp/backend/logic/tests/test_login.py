"""
Autor: Denys Litvynov Lymanets
Fecha: 26-10-2025
Descripción: Tests para LogicaLogin usando BD temporal con SQLAlchemy.
"""

# ---------------------------------------------------------

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...db.models import Base, Usuario
from ...db.database import get_db
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
    
    # Insertar datos de prueba directamente
    hash_test = pwd_context.hash("testpass")
    test_user = Usuario(
        usuario_id=uuid.uuid4(),
        rol_id=1,
        nombre="Test",
        apellido="User",
        correo="test@fake.com",
        contrasena_hash=hash_test
    )
    session.add(test_user)
    session.commit()
    
    yield session
    Base.metadata.drop_all(engine)

# ---------------------------------------------------------

def test_validar_credenciales_correctas(db_session):
    #Si el usuario no se crea y/o no tiene el correo que corresponde - Error
    
    logica = LogicaLogin()
    usuario = logica.validar_credenciales(db_session, "test@fake.com", "testpass")
    assert usuario is not None
    assert usuario.correo == "test@fake.com"

# ---------------------------------------------------------

def test_validar_credenciales_incorrectas(db_session):
    # Si la contraseña es incorrecta - Error

    logica = LogicaLogin()
    usuario = logica.validar_credenciales(db_session, "test@fake.com", "wrongpass")
    assert usuario is None

# ---------------------------------------------------------

def test_generar_token(db_session):
    # Si el token no se ha creado o se ha creado vacio - Error 

    logica = LogicaLogin()
    token = logica.generar_token(str(uuid.uuid4()), 1)
    assert isinstance(token, str)
    assert len(token) > 0

# ---------------------------------------------------------

# ---------------------------------------------------------

# ---------------------------------------------------------
