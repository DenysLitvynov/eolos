"""
Autor: Denys Litvynov Lymanets
Fecha: 27-10-2025
Descripción: Tests para LogicaRegistro usando BD temporal con SQLAlchemy.
"""

# ---------------------------------------------------------

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...db.models import Base, Usuario, Mibisivalencia
from ..registro import LogicaRegistro
import uuid

# ---------------------------------------------------------

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Datos de prueba: Carnet existente (simulado como carnet único)
    carnet_test = Mibisivalencia(
        targeta_id=uuid.uuid4()
    )
    session.add(carnet_test)
    session.commit()
    
    yield session
    Base.metadata.drop_all(engine)

# ---------------------------------------------------------

def test_validar_datos_correctos(db_session):
    # Si la targeta no existe y no da error - Error
    # Si la targeta existe y da error - Error
    logica = LogicaRegistro()
    targeta_id_str = str(uuid.uuid4())  # Nueva, no usada
    with pytest.raises(ValueError):  # Primero falla por targeta no existe
        logica.validar_datos(db_session, "Test", "User", "test@fake.com", targeta_id_str, "pass12345", "pass12345")
    
    # Usar targeta existente
    carnet = db_session.query(Mibisivalencia).first()
    assert logica.validar_datos(db_session, "Test", "User", "test@fake.com", str(carnet.targeta_id), "pass12345", "pass12345") is True

# ---------------------------------------------------------

def test_validar_datos_contrasenas_no_coinciden(db_session):
    logica = LogicaRegistro()
    carnet = db_session.query(Mibisivalencia).first()
    with pytest.raises(ValueError):
        logica.validar_datos(db_session, "Test", "User", "test@fake.com", str(carnet.targeta_id), "pass12345", "wrong")

# ---------------------------------------------------------

def test_validar_datos_targeta_no_existe(db_session):
    logica = LogicaRegistro()
    with pytest.raises(ValueError):
        logica.validar_datos(db_session, "Test", "User", "test@fake.com", str(uuid.uuid4()), "pass12345", "pass12345")

# ---------------------------------------------------------

def test_validar_datos_targeta_ya_usada(db_session):
    logica = LogicaRegistro()
    carnet = db_session.query(Mibisivalencia).first()
    # Agregar usuario con esa targeta
    test_user = Usuario(
        usuario_id=uuid.uuid4(),
        targeta_id=carnet.targeta_id,
        rol_id=1,
        nombre="Existing",
        apellido="User",
        correo="existing@fake.com",
        contrasena_hash="hash"
    )
    db_session.add(test_user)
    db_session.commit()
    
    with pytest.raises(ValueError):
        logica.validar_datos(db_session, "Test", "User", "test@fake.com", str(carnet.targeta_id), "pass12345", "pass12345")
