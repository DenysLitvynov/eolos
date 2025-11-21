"""
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Tests para LogicaResetPassword usando BD temporal en memoria.
"""

# ---------------------------------------------------------

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...db.models import Base, Usuario, Rol, PasswordResetToken
from ..reset_password import LogicaResetPassword
from passlib.context import CryptContext
import uuid
from datetime import datetime, timedelta, UTC

# ---------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Rol de prueba
    rol_usuario = Rol(rol_id=1, nombre="usuario", descripcion="Usuario estándar")
    session.add(rol_usuario)
    session.commit()
    
    # Usuario de prueba
    hash1 = pwd_context.hash("oldpass123!")
    usuario = Usuario(
        usuario_id=str(uuid.uuid4()),
        targeta_id=None,
        nombre="Test",
        apellido="User",
        correo="test@fake.com",
        contrasena_hash=hash1
    )
    usuario.roles.append(rol_usuario)
    session.add(usuario)
    session.commit()
    
    yield session
    session.close()
    Base.metadata.drop_all(engine)

# ---------------------------------------------------------

def test_enviar_reset_token_exitoso(db_session, mocker):
    mock_smtp = mocker.patch('smtplib.SMTP')  # Mock para no enviar real
    
    logica = LogicaResetPassword()
    exito = logica.enviar_reset_token(db_session, "test@fake.com")
    assert exito is True
    
    token = db_session.query(PasswordResetToken).filter(PasswordResetToken.usuario_id == db_session.query(Usuario).first().usuario_id).first()
    assert token is not None
    assert not token.used
    assert len(token.token) > 0
    
    mock_smtp.assert_called()

# ---------------------------------------------------------

def test_resetear_contrasena_exitoso(db_session, mocker):
    mock_smtp = mocker.patch('smtplib.SMTP')
    logica = LogicaResetPassword()
    logica.enviar_reset_token(db_session, "test@fake.com")
    
    token = db_session.query(PasswordResetToken).first().token
    
    exito = logica.resetear_contrasena(db_session, token, "NewPass123!", "NewPass123!")
    assert exito is True
    
    usuario = db_session.query(Usuario).filter(Usuario.correo == "test@fake.com").first()
    assert pwd_context.verify("NewPass123!", usuario.contrasena_hash)
    
    reset_token = db_session.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
    assert reset_token.used is True

# ---------------------------------------------------------

def test_resetear_contrasena_fallido_contrasenas_no_coinciden(db_session, mocker):
    mock_smtp = mocker.patch('smtplib.SMTP')
    logica = LogicaResetPassword()
    logica.enviar_reset_token(db_session, "test@fake.com")
    
    token = db_session.query(PasswordResetToken).first().token
    
    with pytest.raises(ValueError, match="Las contraseñas no coinciden"):
        logica.resetear_contrasena(db_session, token, "NewPass123!", "wrong")

# ---------------------------------------------------------

def test_resetear_contrasena_fallido_token_invalido(db_session, mocker):
    mock_smtp = mocker.patch('smtplib.SMTP')
    logica = LogicaResetPassword()
    
    with pytest.raises(ValueError, match="Token inválido o expirado"):
        logica.resetear_contrasena(db_session, "faketoken", "NewPass123!", "NewPass123!")

# ---------------------------------------------------------
