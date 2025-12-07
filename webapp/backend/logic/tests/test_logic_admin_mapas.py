"""
Autor: Denys Litvynov Lymanets
Fecha: 06-12-2025
Descripción: Tests de integración para la lógica de mapas de administrador.
"""
import pytest
import sys
import os
# Ensure backend importable
sys.path.append(os.getcwd())

from datetime import datetime, date
from backend.logic.logic_admin_mapas import LogicaAdminMapas
from backend.pojos.posicion_gps import PosicionGPS
from backend.db.database import get_db, Base, engine
from backend.db.models import Medida, TipoMedidaEnum

# Setup DB for testing (Functional approach)
@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = next(get_db())
    yield session
    session.close()

def test_obtener_mapa_admin_integration(db):
    """
    Test de integración para verificar que la lógica de admin
    recupera datos correctamente desde la base de datos.
    """
    logica = LogicaAdminMapas()
    
    # 1. Insertar datos fake históricos para probar
    fecha_test = datetime(2023, 1, 1, 12, 0, 0) # Fecha pasada
    lat, lon = 39.0, -0.16
    
    nueva_medida = Medida(
        lectura_id=None, # SQLAlchemy default will trigger if it works, or we can omit. 
        # But wait, default=lambda only works if we don't pass anything or if we pass None and it's handled. 
        # Safest to just not pass it if we want default, or pass a value.
        # Let's pass a value to be explicit since default might not trigger on None depending on SA version.
        # Actually simplest is to omit it.
        tipo=TipoMedidaEnum.no2,
        valor=50.0,
        fecha_hora=fecha_test,
        lat=lat,
        lon=lon
    )
    db.add(nueva_medida)
    db.commit()
    
    # 2. Consultar mapa admin para esa fecha
    inf_izq = PosicionGPS(38.0, -0.3)
    sup_der = PosicionGPS(40.0, 0.0)
    
    # Nota: LogicaAdminMapas.obtener_mapa_admin espera (db, tipo, fecha, lat_min, ...)
    # Y llama a logica_base.obtener_mapa_de_tipo_de_dia_de_destino
    
    # Convertimos a strings/floats como vienen del API
    result = logica.obtener_mapa_admin(
        db, 
        "no2", 
        fecha_test, # datetime
        38.0, -0.3, 40.0, 0.0
    )
    
    # 3. Verificar
    assert "data" in result
    # El resultado está agrupado por horas (int)
    # 12 is the hour of fecha_test
    assert 12 in result["data"]
    points = result["data"][12]
    assert len(points) > 0
    found = False
    for p in points:
        if abs(p["lat"] - lat) < 0.0001 and abs(p["lng"] - lon) < 0.0001:
            assert p["value"] == 50.0
            found = True
            break
    assert found
