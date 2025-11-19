"""
Autor: Denys Litvynov Lymanets
Fecha: 19-11-2025
Descripción: Tests para las clases POJO: PosicionGPS, Trayecto y Medida.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...db.models import Base, Medida as DBMedida, TipoMedidaEnum
from ...pojos.posicion_gps import PosicionGPS
from ...pojos.trayecto import Trayecto
from ...pojos.medida import Medida
from datetime import datetime, timezone
import uuid

# Fixture para BD temporal (solo para Trayecto, que depende de BD)
@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Datos de prueba para medidas
    trayecto_id = str(uuid.uuid4())
    placa_id = str(uuid.uuid4())
    medida1 = DBMedida(
        lectura_id=str(uuid.uuid4()),
        placa_id=placa_id,
        trayecto_id=trayecto_id,
        fecha_hora=datetime.now(timezone.utc),
        tipo=TipoMedidaEnum.pm2_5,
        valor=12.5,
        lat=39.4699,
        lon=-0.3763
    )
    medida2 = DBMedida(
        lectura_id=str(uuid.uuid4()),
        placa_id=placa_id,
        trayecto_id=trayecto_id,
        fecha_hora=datetime.now(timezone.utc),
        tipo=TipoMedidaEnum.temperatura,
        valor=24.8,
        lat=39.4700,
        lon=-0.3764
    )
    session.add_all([medida1, medida2])
    session.commit()

    yield session
    Base.metadata.drop_all(engine)

# ---------------------------------------------------------

def test_posicion_gps_inicializacion():
    pos = PosicionGPS(39.4699, -0.3763)
    assert pos.lat == 39.4699
    assert pos.lon == -0.3763
    
# ---------------------------------------------------------

def test_distancia_entre_dos():
    pos1 = PosicionGPS(39.4699, -0.3763)
    pos2 = PosicionGPS(39.4700, -0.3764)
    dist = PosicionGPS.distancia_entre_dos(pos1, pos2)
    assert dist > 0  # Debe ser positiva
    assert dist < 20  # Aproximadamente pequeña distancia en metros

# ---------------------------------------------------------

def test_obtener_trayecto(db_session):
    trayecto = Trayecto(trayecto_id=db_session.query(DBMedida).first().trayecto_id)
    posiciones = trayecto.obtener_trayecto(db_session)
    assert len(posiciones) == 2  # Dos medidas de prueba
    assert isinstance(posiciones[0], PosicionGPS)

# ---------------------------------------------------------

def test_calcular_distancia(db_session):
    trayecto = Trayecto(trayecto_id=db_session.query(DBMedida).first().trayecto_id)
    distancia = trayecto.calcular_distancia(db_session)
    assert distancia > 0  # Debe ser positiva

# ---------------------------------------------------------

def test_medida_inicializacion():
    pos = PosicionGPS(39.4699, -0.3763)
    medida = Medida(
        trayecto_id=str(uuid.uuid4()),
        placa_id=str(uuid.uuid4()),
        tipo=TipoMedidaEnum.pm2_5,
        valor=12.5,
        fecha_hora=datetime.now(timezone.utc),
        posicion=pos
    )
    assert medida.valor == 12.5
    assert medida.posicion.lat == 39.4699

# ---------------------------------------------------------

def test_obtener_medida():
    pos = PosicionGPS(39.4699, -0.3763)
    medida = Medida(
        trayecto_id=str(uuid.uuid4()),
        placa_id=str(uuid.uuid4()),
        tipo=TipoMedidaEnum.pm2_5,
        valor=12.5,
        fecha_hora=datetime.now(timezone.utc),
        posicion=pos
    )
    dict_medida = medida.obtener_medida()
    assert "valor" in dict_medida
    assert dict_medida["lat"] == 39.4699

# ---------------------------------------------------------
