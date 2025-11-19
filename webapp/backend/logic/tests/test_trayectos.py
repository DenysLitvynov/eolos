"""
Autor: Denys Litvynov Lymanets
Fecha: 19-11-2025
Descripción: Tests para LogicaTrayectos.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...db.models import Base, Usuario, Mibisivalencia, Bicicleta, Estacion, PlacaSensores, Trayecto as DBTrayecto, Medida as DBMedida, EstadoBicicleta, TipoMedidaEnum
from ..trayectos import LogicaTrayectos
from ...pojos.posicion_gps import PosicionGPS
from ...pojos.medida import Medida as DTOMedida
from passlib.context import CryptContext
import uuid
from datetime import datetime, timezone, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Datos de prueba básicos
    targeta_id = "12345678Z"
    carnet = Mibisivalencia(targeta_id=targeta_id)
    session.add(carnet)

    hash_pass = pwd_context.hash("Testpass123!")
    usuario_id = str(uuid.uuid4())
    usuario = Usuario(
        usuario_id=usuario_id,
        targeta_id=targeta_id,
        nombre="Test",
        apellido="User",
        correo="test@fake.com",
        contrasena_hash=hash_pass
    )
    session.add(usuario)

    estacion1 = Estacion(
        estacion_id=1,
        nombre="Test Estacion 1",
        lat=39.4699,
        lon=-0.3763
    )
    session.add(estacion1)

    estacion2 = Estacion(
        estacion_id=2,
        nombre="Test Estacion 2",
        lat=39.4700,
        lon=-0.3764
    )
    session.add(estacion2)

    bicicleta_id = "VLC001"
    bicicleta = Bicicleta(
        bicicleta_id=bicicleta_id,
        estacion_id=1,
        qr_code="QR-VLC001",
        estado=EstadoBicicleta.estacionada
    )
    session.add(bicicleta)

    placa_id = str(uuid.uuid4())
    placa = PlacaSensores(
        placa_id=placa_id,
        bicicleta_id=bicicleta_id,
        estado="activa",
        ult_actualizacion_estado=datetime.utcnow()  # Usar naive UTC para consistencia
    )
    session.add(placa)

    session.commit()
    yield session
    Base.metadata.drop_all(engine)

# Tests para guardar_medida (1-2 tests)
def test_guardar_medida_exitoso(db_session):
    logica = LogicaTrayectos()
    posicion = PosicionGPS(39.4699, -0.3763)
    trayecto_id = str(uuid.uuid4())
    placa = db_session.query(PlacaSensores).first()
    medida_dto = DTOMedida(
        trayecto_id=trayecto_id,
        placa_id=placa.placa_id,
        tipo=TipoMedidaEnum.pm2_5,
        valor=12.5,
        fecha_hora=datetime.utcnow(),
        posicion=posicion
    )
    result = logica.guardar_medida(db_session, medida_dto)
    assert result == "OK"
    saved_medida = db_session.query(DBMedida).filter(DBMedida.trayecto_id == trayecto_id).first()
    assert saved_medida is not None
    assert saved_medida.valor == 12.5

# Tests para iniciar_trayecto (1-2 tests)
def test_iniciar_trayecto_exitoso(db_session):
    logica = LogicaTrayectos()
    posicion = PosicionGPS(39.4699, -0.3763)  # Coincide con estación 1
    trayecto_id = logica.iniciar_trayecto(db_session, "12345678Z", "VLC001", datetime.utcnow(), posicion)
    assert trayecto_id is not None
    assert len(trayecto_id) > 0
    saved_trayecto = db_session.query(DBTrayecto).filter(DBTrayecto.trayecto_id == trayecto_id).first()
    assert saved_trayecto is not None
    assert saved_trayecto.origen_estacion_id == 1

def test_iniciar_trayecto_origen_invalido(db_session):
    logica = LogicaTrayectos()
    posicion_invalida = PosicionGPS(0.0, 0.0)  # No coincide con ninguna estación
    with pytest.raises(RuntimeError):  # Espera RuntimeError ya que envuelve ValueError
        logica.iniciar_trayecto(db_session, "12345678Z", "VLC001", datetime.utcnow(), posicion_invalida)

# Tests para obtener_datos_trayecto (1-2 tests)
def test_obtener_datos_trayecto_exitoso(db_session):
    logica = LogicaTrayectos()
    posicion = PosicionGPS(39.4699, -0.3763)
    trayecto_id = logica.iniciar_trayecto(db_session, "12345678Z", "VLC001", datetime.utcnow(), posicion)
    usuario_id, placa_id = logica.obtener_datos_trayecto(db_session, trayecto_id)
    assert usuario_id is not None
    assert placa_id is not None

def test_obtener_datos_trayecto_no_existente(db_session):
    logica = LogicaTrayectos()
    with pytest.raises(RuntimeError):  # Espera RuntimeError ya que envuelve ValueError
        logica.obtener_datos_trayecto(db_session, "invalid_id")

# Tests para finalizar_trayecto (1-2 tests)
def test_finalizar_trayecto_exitoso_con_distancia(db_session):
    logica = LogicaTrayectos()
    origen = PosicionGPS(39.4699, -0.3763)
    fecha_inicio = datetime.utcnow() - timedelta(minutes=30)
    trayecto_id = logica.iniciar_trayecto(db_session, "12345678Z", "VLC001", fecha_inicio, origen)

    # Agregar medidas de prueba para cálculo de distancia
    placa = db_session.query(PlacaSensores).first()
    medida1 = DBMedida(
        lectura_id=str(uuid.uuid4()),
        placa_id=placa.placa_id,
        trayecto_id=trayecto_id,
        fecha_hora=fecha_inicio + timedelta(minutes=10),
        tipo=TipoMedidaEnum.pm2_5,
        valor=12.5,
        lat=39.4699,
        lon=-0.3763
    )
    medida2 = DBMedida(
        lectura_id=str(uuid.uuid4()),
        placa_id=placa.placa_id,
        trayecto_id=trayecto_id,
        fecha_hora=fecha_inicio + timedelta(minutes=20),
        tipo=TipoMedidaEnum.temperatura,
        valor=24.8,
        lat=39.4700,
        lon=-0.3764
    )
    db_session.add_all([medida1, medida2])
    db_session.commit()

    destino = PosicionGPS(39.4700, -0.3764)
    result = logica.finalizar_trayecto(db_session, trayecto_id, datetime.utcnow(), destino)
    assert result == "OK"

    # Verificar que la distancia se calculó y guardó
    saved_trayecto = db_session.query(DBTrayecto).filter(DBTrayecto.trayecto_id == trayecto_id).first()
    assert saved_trayecto.distancia_total > 0  # Debe ser positiva
    assert saved_trayecto.destino_estacion_id == 2

def test_finalizar_trayecto_sin_medidas(db_session):
    logica = LogicaTrayectos()
    origen = PosicionGPS(39.4699, -0.3763)
    trayecto_id = logica.iniciar_trayecto(db_session, "12345678Z", "VLC001", datetime.utcnow(), origen)
    destino = PosicionGPS(39.4700, -0.3764)
    result = logica.finalizar_trayecto(db_session, trayecto_id, datetime.utcnow(), destino)
    assert result == "OK"
    saved_trayecto = db_session.query(DBTrayecto).filter(DBTrayecto.trayecto_id == trayecto_id).first()
    assert saved_trayecto.distancia_total == 0.0  # Sin medidas, distancia 0

# Tests para actualizar_estado_placa (1-2 tests)
def test_actualizar_estado_placa_exitoso(db_session):
    logica = LogicaTrayectos()
    placa = db_session.query(PlacaSensores).first()
    nuevo_estado = "inactiva"
    nueva_fecha = datetime.utcnow()  # Usar naive UTC
    result = logica.actualizar_estado_placa(db_session, placa.placa_id, nuevo_estado, nueva_fecha)
    assert result == "OK"
    updated_placa = db_session.query(PlacaSensores).filter(PlacaSensores.placa_id == placa.placa_id).first()
    assert updated_placa.estado == nuevo_estado
    # Comparar ignorando microsegundos si es necesario, pero como son naive, debería coincidir
    assert updated_placa.ult_actualizacion_estado.replace(microsecond=0) == nueva_fecha.replace(microsecond=0)

def test_actualizar_estado_placa_no_existente(db_session):
    logica = LogicaTrayectos()
    with pytest.raises(RuntimeError):  # Espera RuntimeError ya que envuelve ValueError
        logica.actualizar_estado_placa(db_session, "invalid_id", "inactiva", datetime.utcnow())

# Tests para actualizar_estado_bici (1-2 tests)
def test_actualizar_estado_bici_exitoso(db_session):
    logica = LogicaTrayectos()
    posicion = PosicionGPS(39.4700, -0.3764)  # Coincide con estación 2
    nuevo_estado = EstadoBicicleta.en_uso
    result = logica.actualizar_estado_bici(db_session, "VLC001", posicion, nuevo_estado)
    assert result == "OK"
    updated_bici = db_session.query(Bicicleta).filter(Bicicleta.bicicleta_id == "VLC001").first()
    assert updated_bici.estacion_id == 2
    assert updated_bici.estado == nuevo_estado

def test_actualizar_estado_bici_posicion_invalida(db_session):
    logica = LogicaTrayectos()
    posicion_invalida = PosicionGPS(0.0, 0.0)
    nuevo_estado = EstadoBicicleta.en_uso
    result = logica.actualizar_estado_bici(db_session, "VLC001", posicion_invalida, nuevo_estado)
    assert result == "OK"  # Debería actualizar estado pero estacion_id a None
    updated_bici = db_session.query(Bicicleta).filter(Bicicleta.bicicleta_id == "VLC001").first()
    assert updated_bici.estacion_id is None
    assert updated_bici.estado == nuevo_estado

# Tests para comprobar_estacion_bici (1-2 tests)
def test_comprobar_estacion_bici_coincidente(db_session):
    logica = LogicaTrayectos()
    posicion = PosicionGPS(39.4699, -0.3763)  # Coincide con estación 1
    estacion_id = logica.comprobar_estacion_bici(db_session, posicion)
    assert estacion_id == 1

def test_comprobar_estacion_bici_no_coincidente(db_session):
    logica = LogicaTrayectos()
    posicion = PosicionGPS(0.0, 0.0)  # No coincide
    estacion_id = logica.comprobar_estacion_bici(db_session, posicion)
    assert estacion_id is None
