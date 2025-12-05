# File: backend/logic/tests/test_mapas.py
"""
Autor: Denys Litvynov Lymanets
Fecha: 04-12-2025
Descripción: Tests para LogicaMapas.
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...db.models import Base, Medida as DBMedida, Interpolada as DBInterpolada, CalidadGeneral, TipoMedidaEnum
from ..mapas import LogicaMapas
from ....pojos.posicion_gps import PosicionGPS
from ....pojos.medida import Medida
import uuid

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    Base.metadata.drop_all(engine)

def test_obtener_mapa_de_tipo_de_dia_de_destino(db_session):
    logica = LogicaMapas()
    dia = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    inf_izq = PosicionGPS(39.0, -0.4)
    sup_der = PosicionGPS(40.0, -0.3)
    result = logica.obtener_mapa_de_tipo_de_dia_de_destino(db_session, "general", dia, inf_izq, sup_der)
    assert "timestamps" in result
    assert len(result["data"]) == 24

def test_obtener_medidas_tipo_fecha_sitio(db_session):
    logica = LogicaMapas()
    fecha = datetime.now(timezone.utc)
    inf_izq = PosicionGPS(39.0, -0.4)
    sup_der = PosicionGPS(40.0, -0.3)
    result = logica.obtener_medidas_tipo_fecha_sitio(db_session, TipoMedidaEnum.pm2_5, fecha, inf_izq, sup_der, False)
    assert isinstance(result, list)

def test_construir_matriz_interpolacion():
    logica = LogicaMapas()
    inf_izq = PosicionGPS(39.0, -0.4)
    sup_der = PosicionGPS(39.001, -0.399)
    result = logica.construir_matriz_interpolacion(inf_izq, sup_der)
    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], PosicionGPS)

def test_interpolar_para_punto():
    logica = LogicaMapas()
    punto = PosicionGPS(39.0, -0.4)
    medidas = [Medida(None, None, TipoMedidaEnum.pm2_5, 10.0, datetime.now(), PosicionGPS(39.0, -0.399))]
    result = logica.interpolar_para_punto(punto, medidas)
    assert isinstance(result, float)

def test_interpolar_para_tipo_fecha(db_session):
    logica = LogicaMapas()
    fecha = datetime.now(timezone.utc).replace(hour=0, minute=0)
    inf_izq = PosicionGPS(39.0, -0.4)
    sup_der = PosicionGPS(39.001, -0.399)
    result = logica.interpolar_para_tipo_fecha(db_session, TipoMedidaEnum.pm2_5, fecha, inf_izq, sup_der)
    assert result == "OK"

def test_unificar_medidas_de_todos_tipos_de_dia(db_session):
    logica = LogicaMapas()
    fecha = datetime.now(timezone.utc)
    inf_izq = PosicionGPS(39.0, -0.4)
    sup_der = PosicionGPS(40.0, -0.3)
    result = logica.unificar_medidas_de_todos_tipos_de_dia(db_session, fecha, inf_izq, sup_der)
    assert isinstance(result, dict)

def test_calcular_calidad_general_del_aire(db_session):
    logica = LogicaMapas()
    fecha = datetime.now(timezone.utc)
    medidas_json = {"0_39.0_-0.4": {"pm2_5": 10.0, "pm10": 20.0}}
    result = logica.calcular_calidad_general_del_aire(db_session, medidas_json, fecha)
    assert result == "OK"

# ---------------------------------------------------------
