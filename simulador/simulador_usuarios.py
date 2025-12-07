"""
Autor: Denys Litvynov Lymanets
Fecha: 03-12-2025
Descripción: Clase para simular usuarios concurrentes que realizan trayectos en bicicleta,
            midiendo la calidad del aire y evaluando el rendimiento del servidor bajo carga.
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
    """
    Simulador de usuarios concurrentes que realizan trayectos reales en bicicleta,
    enviando medidas de calidad del aire y evaluando latencia del backend.
    """

    def __init__(self):
        """
        Inicializa el simulador con configuración base y estructuras para medir rendimiento.
        """
        self.base_url = "http://192.168.1.25:8000/api/v1/trayectos"
        self.response_times = []  # Tiempos individuales de cada petición
        self.lock = threading.Lock()
        self.tipos_medida = ["pm2_5", "pm10", "co", "no2", "o3", "temperatura", "humedad"]

    # ---------------------------------------------------------
    def hacer_peticion_rest(self, method: str, endpoint: str, data: dict = None) -> dict:
        """
        Realiza una petición HTTP y registra el tiempo de respuesta para análisis de rendimiento.

        Args:
            method (str): Método HTTP ('GET', 'POST', 'PUT').
            endpoint (str): Ruta relativa del endpoint.
            data (dict, optional): Datos JSON a enviar en el cuerpo.

        Returns:
            dict: Respuesta parseada en formato JSON.

        Raises:
            requests.HTTPError: Si la petición falla o devuelve código de error.
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, json=data)
            elif method == 'PUT':
                response = requests.put(url, json=data)
            else:
                raise ValueError("Método HTTP no soportado")
            response.raise_for_status()
        finally:
            end_time = time.time()
            with self.lock:
                self.response_times.append(end_time - start_time)
        return response.json()

    # ---------------------------------------------------------
    def simular_x_numero_de_usuarios(self, num_usuarios: int, estaciones: list, bicicletas: list, targetas: list, temporizador: float) -> float:
        """
        Ejecuta simulación concurrente con un número específico de usuarios.

        Args:
            num_usuarios (int): Número de usuarios a simular concurrentemente.
            estaciones (list): Lista de estaciones disponibles.
            bicicletas (list): Lista de bicicletas disponibles.
            targetas (list): Lista de IDs de tarjetas de usuario.
            temporizador (float): Intervalo en segundos entre medidas de cada usuario.

        Returns:
            float: Tiempo medio de respuesta por petición (en segundos).
        """
        self.response_times = []  # Reiniciar métricas
        threads = []
        for _ in range(num_usuarios):
            targeta_id = random.choice(targetas)
            thread = threading.Thread(
                target=self.simular_ruta_en_bici,
                args=(temporizador, targeta_id, estaciones, bicicletas)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return sum(self.response_times) / len(self.response_times) if self.response_times else 0.0

    # ---------------------------------------------------------
    def simular_ruta_en_bici(self, temporizador: float, targeta_id: str, estaciones: list, bicicletas: list) -> None:
        """
        Simula el trayecto completo de un usuario: inicio, medidas en ruta y finalización.

        Args:
            temporizador (float): Tiempo de espera entre cada medida (segundos).
            targeta_id (str): ID de la tarjeta del usuario.
            estaciones (list): Lista de estaciones disponibles.
            bicicletas (list): Lista de bicicletas disponibles.
        """
        estacion_inicio = random.choice(estaciones)
        estacion_final = random.choice([e for e in estaciones if e['estacion_id'] != estacion_inicio['estacion_id']])
        bici_escogida = random.choice(bicicletas)
        posicion_actual = {'lat': estacion_inicio['lat'], 'lon': estacion_inicio['lon']}

        # Iniciar trayecto
        trayecto = self.hacer_peticion_rest('POST', "/iniciar-trayecto", {
            "targeta_id": targeta_id,
            "bicicleta_id": bici_escogida['bicicleta_id'],
            "fecha_inicio": datetime.utcnow().isoformat(),
            "origen": posicion_actual
        })
        trayecto_id = trayecto['trayecto_id']
        placa_id = self.hacer_peticion_rest('GET', f"/obtener-datos-trayecto/{trayecto_id}")['placa_id']

        # Marcar bici como en uso
        self.hacer_peticion_rest('PUT', "/actualizar-estado-bici", {
            "bicicleta_id": bici_escogida['bicicleta_id'],
            "posicion": posicion_actual,
            "estado": "en_uso"
        })

        contador = 0
        while True:
            if self.haversine(posicion_actual, estacion_final) <= 100:
                posicion_actual = estacion_final.copy()
                break

            posicion_actual = self.obtener_punto_en_cien_metros(posicion_actual, estacion_final)
            time.sleep(temporizador)

            # Enviar medida
            self.hacer_peticion_rest('POST', "/guardar-medida", {
                "trayecto_id": trayecto_id,
                "placa_id": placa_id,
                "tipo": random.choice(self.tipos_medida),
                "valor": random.uniform(10, 50),
                "fecha_hora": datetime.utcnow().isoformat(),
                "posicion": posicion_actual
            })

            contador += 1
            if contador % 10 == 0:
                self.hacer_peticion_rest('PUT', "/actualizar-estado-placa", {
                    "placa_id": placa_id,
                    "estado": "activa",
                    "ult_actualizacion_estado": datetime.utcnow().isoformat()
                })

        # Finalizar trayecto
        self.hacer_peticion_rest('PUT', "/actualizar-estado-bici", {
            "bicicleta_id": bici_escogida['bicicleta_id'],
            "posicion": posicion_actual,
            "estado": "estacionada"
        })

        self.hacer_peticion_rest('PUT', "/finalizar-trayecto", {
            "trayecto_id": trayecto_id,
            "fecha_fin": datetime.utcnow().isoformat(),
            "destino": posicion_actual
        })

    # ---------------------------------------------------------
    def obtener_punto_en_cien_metros(self, pos_actual: dict, est_final: dict) -> dict:
        """
        Calcula el siguiente punto a ~100 metros del actual, en dirección al destino,
        con variación aleatoria de ±30° para simular trayectos naturales.

        Args:
            pos_actual (dict): Posición actual del usuario {'lat': float, 'lon': float}.
            est_final (dict): Posición de la estación destino.

        Returns:
            dict: Nueva posición avanzada ~100 metros.
        """
        if self.haversine(pos_actual, est_final) <= 100:
            return est_final.copy()

        bearing_principal = self.bearing(pos_actual, est_final)
        desviacion = math.radians(random.uniform(-30, 30))
        nuevo_bearing = bearing_principal + desviacion
        return self.move_point(pos_actual, 100, nuevo_bearing)

    # ---------------------------------------------------------
    def obtener_temporizador_medidas(self, num_usuarios: int) -> float:
        """
        Calcula el intervalo entre medidas para mantener una carga constante
        independientemente del número de usuarios concurrentes.

        Args:
            num_usuarios (int): Número de usuarios simulados.

        Returns:
            float: Intervalo en segundos entre medidas por usuario.
        """
        base_interval = 27.7  # 10ms base → ajustable para stress
        return base_interval / max(num_usuarios, 1)

    # ---------------------------------------------------------
    def dibujar_grafica(self, data: dict) -> None:
        """
        Genera y guarda una gráfica de latencia media vs número de usuarios concurrentes.

        Args:
            data (dict): Diccionario con clave = número de usuarios, valor = latencia media.
        """
        x = sorted(data.keys())
        y = [data[k] for k in x]
        plt.figure(figsize=(10, 6))
        plt.plot(x, y, marker='o', linestyle='-', color='b', linewidth=2)
        plt.xlabel('Número de usuarios concurrentes')
        plt.ylabel('Latencia media por petición (segundos)')
        plt.title('Rendimiento del servidor bajo carga creciente')
        plt.grid(True, alpha=0.3)
        plt.savefig('grafica_latency.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Gráfica guardada como 'grafica_latency.png'")

    # ---------------------------------------------------------
    def leer_de_un_json(self, filename: str) -> list:
        """
        Carga datos desde un archivo JSON (estaciones, bicicletas, tarjetas, etc.).

        Args:
            filename (str): Ruta del archivo JSON.

        Returns:
            list: Lista de objetos leídos del JSON.
        """
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    # ---------------------------------------------------------
    def haversine(self, p1: dict, p2: dict) -> float:
        """
        Calcula distancia en metros entre dos puntos GPS usando fórmula de Haversine.

        Args:
            p1 (dict): Primer punto {'lat': float, 'lon': float}.
            p2 (dict): Segundo punto.

        Returns:
            float: Distancia en metros.
        """
        lat1, lon1 = math.radians(p1['lat']), math.radians(p1['lon'])
        lat2, lon2 = math.radians(p2['lat']), math.radians(p2['lon'])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return 6371000 * c

    # ---------------------------------------------------------
    def bearing(self, p1: dict, p2: dict) -> float:
        """
        Calcula el rumbo (bearing) en radianes desde p1 hacia p2.

        Args:
            p1 (dict): Punto origen.
            p2 (dict): Punto destino.

        Returns:
            float: Ángulo en radianes (bearing).
        """
        lat1, lon1 = math.radians(p1['lat']), math.radians(p1['lon'])
        lat2, lon2 = math.radians(p2['lat']), math.radians(p2['lon'])
        dlon = lon2 - lon1
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        return math.atan2(y, x)

    # ---------------------------------------------------------
    def move_point(self, p: dict, distance: float, bearing: float) -> dict:
        """
        Mueve un punto una distancia dada en una dirección (bearing) dada.

        Args:
            p (dict): Punto inicial {'lat': float, 'lon': float}.
            distance (float): Distancia a avanzar en metros.
            bearing (float): Dirección en radianes.

        Returns:
            dict: Nuevo punto tras el desplazamiento.
        """
        R = 6371000
        lat1 = math.radians(p['lat'])
        lon1 = math.radians(p['lon'])
        lat2 = math.asin(math.sin(lat1) * math.cos(distance / R) +
                         math.cos(lat1) * math.sin(distance / R) * math.cos(bearing))
        lon2 = lon1 + math.atan2(math.sin(bearing) * math.sin(distance / R) * math.cos(lat1),
                                 math.cos(distance / R) - math.sin(lat1) * math.sin(lat2))
        return {'lat': math.degrees(lat2), 'lon': math.degrees(lon2)}
