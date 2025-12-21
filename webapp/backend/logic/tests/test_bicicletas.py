# File: backend/logic/tests/test_bicicletas.py
"""
Autor: Hugo Belda Revert
Fecha: 21-12-2025
Descripción: Tests unitarios para la clase LogicaBicicletas.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...db.models import Base, Estacion, Bicicleta, EstadoBicicleta
from ..bicicletas import LogicaBicicletas

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

def test_obtener_estaciones(db_session):
    """
    Verifica que obtener_estaciones recupera correctamente las estaciones
    y calcula las bicicletas disponibles y los huecos libres.
    """
    # 1. Preparar datos de prueba
    estacion1 = Estacion(
        nombre="Estacion 1",
        lat=39.47,
        lon=-0.37,
        capacidad=10
    )
    estacion2 = Estacion(
        nombre="Estacion 2",
        lat=39.48,
        lon=-0.38,
        capacidad=5
    )
    db_session.add(estacion1)
    db_session.add(estacion2)
    db_session.commit()

    # Añadir bicicletas a la estación 1
    # 3 estacionadas, 1 en uso (no cuenta como disponible en la estación)
    bici1 = Bicicleta(bicicleta_id="b1", estacion_id=estacion1.estacion_id, qr_code="qr1", estado=EstadoBicicleta.estacionada)
    bici2 = Bicicleta(bicicleta_id="b2", estacion_id=estacion1.estacion_id, qr_code="qr2", estado=EstadoBicicleta.estacionada)
    bici3 = Bicicleta(bicicleta_id="b3", estacion_id=estacion1.estacion_id, qr_code="qr3", estado=EstadoBicicleta.estacionada)
    bici4 = Bicicleta(bicicleta_id="b4", estacion_id=estacion1.estacion_id, qr_code="qr4", estado=EstadoBicicleta.en_uso)
    
    # Añadir bicicletas a la estación 2
    # 5 estacionadas (llena)
    for i in range(5):
        b = Bicicleta(bicicleta_id=f"b2_{i}", estacion_id=estacion2.estacion_id, qr_code=f"qr2_{i}", estado=EstadoBicicleta.estacionada)
        db_session.add(b)

    db_session.add_all([bici1, bici2, bici3, bici4])
    db_session.commit()

    # 2. Ejecutar la lógica
    logica = LogicaBicicletas()
    resultado = logica.obtener_estaciones(db_session)

    # 3. Verificar resultados
    assert len(resultado) == 2
    
    # Verificar Estacion 1
    e1 = next(e for e in resultado if e["name"] == "Estacion 1")
    assert e1["available_bikes"] == 3
    assert e1["total_stands"] == 10
    assert e1["available_stands"] == 7 # 10 - 3
    assert e1["lat"] == 39.47
    assert e1["lon"] == -0.37

    # Verificar Estacion 2
    e2 = next(e for e in resultado if e["name"] == "Estacion 2")
    assert e2["available_bikes"] == 5
    assert e2["total_stands"] == 5
    assert e2["available_stands"] == 0 # 5 - 5
