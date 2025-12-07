# File: backend/logic/tests/test_mapas.py
"""
Autor: Denys Litvynov Lymanets
Fecha: 04-12-2025
Descripción: Tests unitarios para la clase LogicaMapas.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...db.models import Base, Medida as DBMedida, Interpolada as DBInterpolada, CalidadGeneral, TipoMedidaEnum
from ..mapas import LogicaMapas
from ....pojos.posicion_gps import PosicionGPS
from ....pojos.medida import Medida


@pytest.fixture(scope="function")
def db_session():
    """Crea una base de datos en memoria SQLite y proporciona una sesión limpia para cada test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


# ---------------------------------------------------------
def test_obtener_mapa_de_tipo_de_dia_de_destino(db_session):
    """
    Verifica que el método obtener_mapa_de_tipo_de_dia_de_destino devuelve la estructura
    esperada para el mapa general: un diccionario con clave 'data' que contiene 24 horas.
    """
    logica = LogicaMapas()
    dia = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    inf_izq = PosicionGPS(39.0, -0.4)
    sup_der = PosicionGPS(40.0, -0.3)
    result = logica.obtener_mapa_de_tipo_de_dia_de_destino(db_session, "general", dia, inf_izq, sup_der)
    assert isinstance(result, dict)
    assert "data" in result
    assert isinstance(result["data"], dict)
    assert len(result["data"]) <= 24  # Puede haber menos si no hay datos


# ---------------------------------------------------------
def test_obtener_medidas_tipo_fecha_sitio(db_session):
    """
    Comprueba que obtener_medidas_tipo_fecha_sitio devuelve una lista (incluso vacía)
    cuando no existen medidas reales para el tipo y zona solicitada.
    """
    logica = LogicaMapas()
    fecha = datetime.now(timezone.utc)
    inf_izq = PosicionGPS(39.0, -0.4)
    sup_der = PosicionGPS(40.0, -0.3)
    result = logica.obtener_medidas_tipo_fecha_sitio(db_session, TipoMedidaEnum.pm2_5, fecha, inf_izq, sup_der, False)
    assert isinstance(result, list)


# ---------------------------------------------------------
def test_construir_matriz_interpolacion():
    """
    Asegura que construir_matriz_interpolacion genera una lista no vacía de objetos
    PosicionGPS dentro del bounding box especificado.
    """
    logica = LogicaMapas()
    inf_izq = PosicionGPS(39.0, -0.4)
    sup_der = PosicionGPS(39.001, -0.399)
    result = logica.construir_matriz_interpolacion(inf_izq, sup_der)
    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], PosicionGPS)


# ---------------------------------------------------------
def test_interpolar_para_punto():
    """
    Verifica que la interpolación IDW devuelve un valor float cuando hay medidas cercanas
    y maneja correctamente puntos muy próximos.
    """
    logica = LogicaMapas()
    punto = PosicionGPS(39.0, -0.4)
    medidas = [
        Medida(None, None, TipoMedidaEnum.pm2_5, 10.0, datetime.now(timezone.utc),
               PosicionGPS(39.0, -0.399))
    ]
    result = logica.interpolar_para_punto(punto, medidas)
    assert isinstance(result, float)


# ---------------------------------------------------------
def test_interpolar_para_tipo_fecha(db_session):
    """
    Comprueba que interpolar_para_tipo_fecha completa el proceso sin lanzar excepciones
    y devuelve "OK" cuando no hay medidas que impidan la ejecución.
    """
    logica = LogicaMapas()
    fecha = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    inf_izq = PosicionGPS(39.0, -0.4)
    sup_der = PosicionGPS(39.001, -0.399)
    result = logica.interpolar_para_tipo_fecha(db_session, TipoMedidaEnum.pm2_5, fecha, inf_izq, sup_der)
    assert result == "OK"


# ---------------------------------------------------------
def test_unificar_medidas_de_todos_tipos_de_dia(db_session):
    """
    Asegura que la unificación de medidas de todos los contaminantes devuelve un diccionario,
    incluso cuando la base de datos está vacía.
    """
    logica = LogicaMapas()
    fecha = datetime.now(timezone.utc)
    inf_izq = PosicionGPS(39.0, -0.4)
    sup_der = PosicionGPS(40.0, -0.3)
    result = logica.unificar_medidas_de_todos_tipos_de_dia(db_session, fecha, inf_izq, sup_der)
    assert isinstance(result, dict)


# ---------------------------------------------------------
def test_calcular_calidad_general_del_aire(db_session):
    """
    Verifica que el cálculo de calidad general del aire se completa correctamente,
    almacena los registros en la tabla CalidadGeneral y devuelve "OK".
    """
    logica = LogicaMapas()
    fecha = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    medidas_json = {"0_39.0_-0.4": {"pm2_5": 10.0, "pm10": 20.0}}
    result = logica.calcular_calidad_general_del_aire(db_session, medidas_json, fecha)
    assert result == "OK"

    # Opcional: verificar que realmente se insertó algo
    count = db_session.query(CalidadGeneral).count()
    assert count > 0

# ---------------------------------------------------------
