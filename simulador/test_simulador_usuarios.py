"""
Autor: Denys Litvynov Lymanets
Fecha: 03-12-2025
Descripción: Tests unitarios para el simulador de usuarios.
"""

import pytest
from simulador_usuarios import SimuladorUsuarios
from math import isclose


@pytest.fixture
def sim():
    """Proporciona una instancia limpia del simulador para cada test."""
    return SimuladorUsuarios()


# ---------------------------------------------------------
def test_obtener_temporizador_medidas(sim):
    """
    Verifica que el temporizador se escala correctamente con el número de usuarios.
    """
    assert isclose(sim.obtener_temporizador_medidas(1), 0.01, abs_tol=0.001)
    assert isclose(sim.obtener_temporizador_medidas(200), 0.01 / 200, abs_tol=0.00001)


# ---------------------------------------------------------
def test_obtener_punto_en_cien_metros_cerca(sim):
    """
    Comprueba que si el destino está a menos de 100m, se devuelve directamente.
    """
    pos_actual = {'lat': 39.4699, 'lon': -0.3763}
    est_final = {'lat': 39.4699, 'lon': -0.3763}
    new_pos = sim.obtener_punto_en_cien_metros(pos_actual, est_final)
    assert new_pos == est_final


# ---------------------------------------------------------
def test_obtener_punto_en_cien_metros_lejos(sim):
    """
    Verifica que cuando hay distancia suficiente, el punto avanzado está a ~100m.
    """
    pos_actual = {'lat': 39.4699, 'lon': -0.3763}
    est_final = {'lat': 39.4780, 'lon': -0.3266}
    new_pos = sim.obtener_punto_en_cien_metros(pos_actual, est_final)
    dist = sim.haversine(pos_actual, new_pos)
    assert isclose(dist, 100, abs_tol=15)  # Tolerancia por desviación aleatoria
