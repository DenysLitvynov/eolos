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
from datetime import datetime, timedelta, UTC

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
    session.commit()  # Commit roles
    
    # Mibisivalencias (carnets)
    carnet1 = Mibisivalencia(targeta_id="12345678A")
    carnet2 = Mibisivalencia(targeta_id="87654321B")
    session.add(carnet1)
    session.add(carnet2)
    
    # Usuarios
    hash1 = pwd_context.hash("Password123!")
    usuario1 = Usuario(
        usuario_id=str(uuid.uuid4()),
        targeta_id="12345678A",
        nombre="Usuario",
        apellido="Prueba1",
        correo="prueba1@fake.com",
        contrasena_hash=hash1
    )
    usuario1.roles.append(rol_usuario)  # Asignar rol
    hash2 = pwd_context.hash("Admin123!")
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
    """
    Test: validar datos correctos con carnet no usado
    """
    logica = LogicaRegistro()
    # Usar carnet no usado del fixture (carnet2: 87654321B)
    assert logica.validar_datos(db_session, "Test", "User", "test@fake.com", "87654321B", "Pass123!", "Pass123!", True) is True

# ---------------------------------------------------------

def test_validar_datos_contrasenas_no_coinciden(db_session):
    """
    Test: Fallo si contraseñas no coinciden
    """
    logica = LogicaRegistro()
    with pytest.raises(ValueError):
        logica.validar_datos(db_session, "Test", "User", "test@fake.com", "87654321B", "Pass123!", "wrong", True)

# ---------------------------------------------------------

def test_validar_datos_targeta_no_existe(db_session):
    """
    Test: fallo si carnet no existe en mibisivalencia
    """
    logica = LogicaRegistro()
    with pytest.raises(ValueError):
        logica.validar_datos(db_session, "Test", "User", "test@fake.com", "99999999X", "Pass123!", "Pass123!", True)

# ---------------------------------------------------------

def test_validar_datos_targeta_ya_usada(db_session):
    """
    Test: Fallo si carnet ya asociado a usuario
    """
    logica = LogicaRegistro()
    # Usar carnet ya asociado (12345678A usado por usuario1)
    with pytest.raises(ValueError):
        logica.validar_datos(db_session, "Test", "User", "test@fake.com", "12345678A", "Pass123!", "Pass123!", True)

# ---------------------------------------------------------

def test_iniciar_registro_exitoso(db_session, mocker):
    """
    Test: Iniciar registro exitoso y verificar pendiente
    """
    mocker.patch.object(LogicaRegistro, 'generar_codigo_verificacion', return_value="123456")
    mock_enviar = mocker.patch.object(LogicaRegistro, 'enviar_email_verificacion', return_value=True)
    
    logica = LogicaRegistro()
    exito = logica.iniciar_registro(db_session, "Nuevo", "Usuario", "nuevo@fake.com", "87654321B", "Pass123!", "Pass123!", True)
    assert exito is True
    
    pendiente = db_session.query(PendingRegistration).filter(PendingRegistration.correo == "nuevo@fake.com").first()
    assert pendiente is not None
    assert pendiente.verification_code == "123456"
    assert pwd_context.verify("Pass123!", pendiente.contrasena_hash) is True  # Verificar en lugar de comparar hash
    
    mock_enviar.assert_called_once_with("nuevo@fake.com", "123456")

# ---------------------------------------------------------

def test_reenviar_codigo_exitoso(db_session, mocker):
    """
    Test: reenviar código exitoso
    """
    # Primero inicia un registro
    mocker.patch.object(LogicaRegistro, 'generar_codigo_verificacion', return_value="123456")
    mock_enviar = mocker.patch.object(LogicaRegistro, 'enviar_email_verificacion', return_value=True)
    
    logica = LogicaRegistro()
    logica.iniciar_registro(db_session, "Nuevo", "Usuario", "nuevo@fake.com", "87654321B", "Pass123!", "Pass123!", True)
    
    # Reenviar (mock nuevo código)
    mocker.patch.object(LogicaRegistro, 'generar_codigo_verificacion', return_value="654321")
    
    exito = logica.reenviar_codigo(db_session, "nuevo@fake.com")
    assert exito is True
    
    pendiente = db_session.query(PendingRegistration).filter(PendingRegistration.correo == "nuevo@fake.com").first()
    assert pendiente.verification_code == "654321"
    
    assert mock_enviar.call_count == 2  # Uno inicial, uno reenviar
    mock_enviar.assert_called_with("nuevo@fake.com", "654321")

# ---------------------------------------------------------

def test_verificar_y_completar_exitoso(db_session, mocker):
    """
    Test: verificar código y completar registro exitoso
    """
    mocker.patch.object(LogicaRegistro, 'generar_codigo_verificacion', return_value="123456")
    mocker.patch.object(LogicaRegistro, 'enviar_email_verificacion', return_value=True)
    
    logica = LogicaRegistro()
    logica.iniciar_registro(db_session, "Nuevo", "Usuario", "nuevo@fake.com", "87654321B", "Pass123!", "Pass123!", True)
    
    token = logica.verificar_y_completar(db_session, "nuevo@fake.com", "123456")
    assert isinstance(token, str)
    
    usuario = db_session.query(Usuario).filter(Usuario.correo == "nuevo@fake.com").first()
    assert usuario is not None
    assert usuario.targeta_id == "87654321B"
    assert "usuario" in [rol.nombre for rol in usuario.roles]
    
    pendiente = db_session.query(PendingRegistration).filter(PendingRegistration.correo == "nuevo@fake.com").first()
    assert pendiente is None  # Borrado

# ---------------------------------------------------------

