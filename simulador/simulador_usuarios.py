"""
Autor: Denys Litvynov Lymanets
Fecha: 03-12-2025
Descripción: Clase para simular usuarios realizando trayectos y midiendo el rendimiento del servidor.
"""

import requests
import time
import random
import math
import threading
import json
import matplotlib.pyplot as plt
from datetime import datetime

class SimuladorUsuarios:
    def __init__(self):
        """
        Inicializa el simulador con variables compartidas para mediciones.
        """
        self.base_url = "http://192.168.1.25:8000/api/v1/trayectos"
        self.response_times = []  # Nueva lista para tiempos de respuesta individuales
        self.lock = threading.Lock()
        self.tipos_medida = ["pm2_5", "pm10", "co", "no2", "o3", "temperatura", "humedad"]

    def hacer_peticion_rest(self, method: str, endpoint: str, data: dict = None) -> dict:
        """
        Realiza una petición REST genérica y registra el tiempo de respuesta.

        Args:
            method (str): Método HTTP ('GET', 'POST', 'PUT').
            endpoint (str): Endpoint relativo.
            data (dict): Datos JSON para enviar (opcional).

        Returns:
            dict: Respuesta JSON.
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data)
        elif method == 'PUT':
            response = requests.put(url, json=data)
        else:
            raise ValueError("Método no soportado")
        response.raise_for_status()
        end_time = time.time()
        with self.lock:
            self.response_times.append(end_time - start_time)
        return response.json()

    def simular_x_numero_de_usuarios(self, num_usuarios: int, estaciones: list, bicicletas: list, targetas: list, temporizador: float) -> float:
        """
        Simula un número dado de usuarios concurrentes.

        Args:
            num_usuarios (int): Número de usuarios a simular.
            estaciones (list): Lista de estaciones.
            bicicletas (list): Lista de bicicletas.
            targetas (list): Lista de targetas ID.
            temporizador (float): Tiempo entre mediciones por usuario.

        Returns:
            float: Tiempo de respuesta promedio por petición.
        """
        self.response_times = []  # Resetear tiempos
        threads = []
        for _ in range(num_usuarios):
            targeta_id = random.choice(targetas)
            thread = threading.Thread(target=self.simular_ruta_en_bici, args=(temporizador, targeta_id, estaciones, bicicletas))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        if self.response_times:
            average = sum(self.response_times) / len(self.response_times)
        else:
            average = 0.0
        return average

    def simular_ruta_en_bici(self, temporizador: float, targeta_id: str, estaciones: list, bicicletas: list) -> list:
        """
        Simula la ruta de un usuario en bicicleta, realizando peticiones API.

        Args:
            temporizador (float): Tiempo entre mediciones.
            targeta_id (str): ID de la targeta.
            estaciones (list): Lista de estaciones.
            bicicletas (list): Lista de bicicletas.

        Returns:
            list: Lista de tiempos entre peticiones de este usuario (duraciones de respuesta).
        """
        user_times = []
        estacion_inicio = random.choice(estaciones)
        estacion_final = random.choice([e for e in estaciones if e['estacion_id'] != estacion_inicio['estacion_id']])
        bici_escogida = random.choice(bicicletas)
        posicion_actual = {'lat': estacion_inicio['lat'], 'lon': estacion_inicio['lon']}
        # Iniciar trayecto
        init_data = {
            "targeta_id": targeta_id,
            "bicicleta_id": bici_escogida['bicicleta_id'],
            "fecha_inicio": datetime.utcnow().isoformat(),
            "origen": {"lat": posicion_actual['lat'], "lon": posicion_actual['lon']}
        }
        trayecto = self.hacer_peticion_rest('POST', "/iniciar-trayecto", init_data)
        trayecto_id = trayecto['trayecto_id']
        # Obtener datos
        datos = self.hacer_peticion_rest('GET', f"/obtener-datos-trayecto/{trayecto_id}")
        placa_id = datos['placa_id']
        # Actualizar estado bici (en uso)
        bici_data = {
            "bicicleta_id": bici_escogida['bicicleta_id'],
            "posicion": {"lat": posicion_actual['lat'], "lon": posicion_actual['lon']},
            "estado": "en_uso"
        }
        self.hacer_peticion_rest('PUT', "/actualizar-estado-bici", bici_data)
        # Bucle de trayecto
        contador = 0
        while True:
            dist = self.haversine(posicion_actual, estacion_final)
            if dist <= 100:
                posicion_actual = estacion_final.copy()
                break
            posicion_actual = self.obtener_punto_en_cien_metros(posicion_actual, estacion_final)
            time.sleep(temporizador)
            # Guardar medida
            medida_data = {
                "trayecto_id": trayecto_id,
                "placa_id": placa_id,
                "tipo": random.choice(self.tipos_medida),
                "valor": random.uniform(10, 50),
                "fecha_hora": datetime.utcnow().isoformat(),
                "posicion": {"lat": posicion_actual['lat'], "lon": posicion_actual['lon']}
            }
            self.hacer_peticion_rest('POST', "/guardar-medida", medida_data)
            contador += 1
            if contador % 10 == 0:
                placa_data = {
                    "placa_id": placa_id,
                    "estado": "activa",
                    "ult_actualizacion_estado": datetime.utcnow().isoformat()
                }
                self.hacer_peticion_rest('PUT', "/actualizar-estado-placa", placa_data)
        # Actualizar estado bici (estacionada)
        bici_data = {
            "bicicleta_id": bici_escogida['bicicleta_id'],
            "posicion": {"lat": posicion_actual['lat'], "lon": posicion_actual['lon']},
            "estado": "estacionada"
        }
        self.hacer_peticion_rest('PUT', "/actualizar-estado-bici", bici_data)
        # Finalizar trayecto
        fin_data = {
            "trayecto_id": trayecto_id,
            "fecha_fin": datetime.utcnow().isoformat(),
            "destino": {"lat": posicion_actual['lat'], "lon": posicion_actual['lon']}
        }
        self.hacer_peticion_rest('PUT', "/finalizar-trayecto", fin_data)
        return user_times

    def obtener_punto_en_cien_metros(self, pos_actual: dict, est_final: dict) -> dict:
        """
        Obtiene el siguiente punto a 100 metros en dirección al destino, con variación de 60 grados.

        Args:
            pos_actual (dict): Posición actual {'lat': float, 'lon': float}.
            est_final (dict): Posición final {'lat': float, 'lon': float}.

        Returns:
            dict: Nueva posición.
        """
        dist = self.haversine(pos_actual, est_final)
        if dist <= 100:
            return est_final.copy()
        main_bearing = self.bearing(pos_actual, est_final)
        offset = math.radians(random.uniform(-30, 30))
        new_bearing = main_bearing + offset
        new_pos = self.move_point(pos_actual, 100, new_bearing)
        return new_pos

    def obtener_temporizador_medidas(self, num_usuarios: int) -> float:
        """
        Calcula el temporizador para el intervalo entre medidas basado en el número de usuarios.

        Args:
            num_usuarios (int): Número de usuarios.

        Returns:
            float: Temporizador en segundos.
        """
        base_interval = 0.01  # Cambiado a bajo para stress test (ajusta más bajo si quieres saturar)
        return base_interval / num_usuarios if num_usuarios > 0 else base_interval

    def dibujar_grafica(self, data: dict) -> None:
        """
        Dibuja y guarda una gráfica de tiempo medio de respuesta vs. número de usuarios.

        Args:
            data (dict): Diccionario {num_usuarios: tiempo_medio}.

        Returns:
            None
        """
        x = sorted(data.keys())
        y = [data[k] for k in x]
        plt.figure()
        plt.plot(x, y)
        plt.xlabel('Número de usuarios')
        plt.ylabel('Tiempo medio de respuesta por petición (s)')
        plt.title('Rendimiento del servidor bajo carga (Latency)')
        plt.savefig('grafica_latency.png')
        plt.close()

    def leer_de_un_json(self, filename: str) -> list:
        """
        Lee datos de un archivo JSON.

        Args:
            filename (str): Nombre del archivo JSON.

        Returns:
            list: Datos leídos.
        """
        with open(filename, 'r') as f:
            return json.load(f)

    # Funciones auxiliares para cálculos geográficos
    def haversine(self, p1: dict, p2: dict) -> float:
        """
        Calcula la distancia en metros entre dos puntos GPS.

        Args:
            p1 (dict): Punto 1.
            p2 (dict): Punto 2.

        Returns:
            float: Distancia en metros.
        """
        lat1 = math.radians(p1['lat'])
        lon1 = math.radians(p1['lon'])
        lat2 = math.radians(p2['lat'])
        lon2 = math.radians(p2['lon'])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return 6371000 * c

    def bearing(self, p1: dict, p2: dict) -> float:
        """
        Calcula el bearing en radianes entre dos puntos.

        Args:
            p1 (dict): Punto 1.
            p2 (dict): Punto 2.

        Returns:
            float: Bearing en radianes.
        """
        lat1 = math.radians(p1['lat'])
        lon1 = math.radians(p1['lon'])
        lat2 = math.radians(p2['lat'])
        lon2 = math.radians(p2['lon'])
        dlon = lon2 - lon1
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        return math.atan2(y, x)

    def move_point(self, p: dict, distance: float, bearing: float) -> dict:
        """
        Mueve un punto una distancia dada en un bearing dado.

        Args:
            p (dict): Punto inicial.
            distance (float): Distancia en metros.
            bearing (float): Bearing en radianes.

        Returns:
            dict: Nuevo punto.
        """
        R = 6371000
        lat1 = math.radians(p['lat'])
        lon1 = math.radians(p['lon'])
        lat2 = math.asin(math.sin(lat1) * math.cos(distance / R) + math.cos(lat1) * math.sin(distance / R) * math.cos(bearing))
        lon2 = lon1 + math.atan2(math.sin(bearing) * math.sin(distance / R) * math.cos(lat1),
                                 math.cos(distance / R) - math.sin(lat1) * math.sin(lat2))
        return {'lat': math.degrees(lat2), 'lon': math.degrees(lon2)}
