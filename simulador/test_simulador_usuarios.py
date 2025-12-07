import pytest
from simulador_usuarios import SimuladorUsuarios
from math import isclose

@pytest.fixture
def sim():
    return SimuladorUsuarios()

def test_obtener_temporizador_medidas(sim):
    assert isclose(sim.obtener_temporizador_medidas(1), 27.7, abs_tol=0.1)
    assert isclose(sim.obtener_temporizador_medidas(200), 27.7 / 200, abs_tol=0.001)

def test_obtener_punto_en_cien_metros_cerca(sim):
    pos_actual = {'lat': 39.4699, 'lon': -0.3763}
    est_final = {'lat': 39.4699, 'lon': -0.3763}  # Mismo punto
    new_pos = sim.obtener_punto_en_cien_metros(pos_actual, est_final)
    assert new_pos == est_final

def test_obtener_punto_en_cien_metros_lejos(sim):
    pos_actual = {'lat': 39.4699, 'lon': -0.3763}
    est_final = {'lat': 39.4780, 'lon': -0.3266}
    new_pos = sim.obtener_punto_en_cien_metros(pos_actual, est_final)
    dist = sim.haversine(pos_actual, new_pos)
    assert isclose(dist, 100, abs_tol=1)

