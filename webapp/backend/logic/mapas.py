"""
Autor: Denys Litvynov Lymanets
Fecha: 04-12-2025
Descripción: Lógica de negocio para mapas de calidad del aire.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict
import uuid
from math import inf
from sqlalchemy.orm import Session
from sqlalchemy import union_all, func
from ..db.models import Medida as DBMedida, Interpolada as DBInterpolada, CalidadGeneral, TipoMedidaEnum
from ..pojos.medida import Medida
from ..pojos.posicion_gps import PosicionGPS

class LogicaMapas:

    # Tipos de gases considerados
    GASES = [TipoMedidaEnum.pm2_5, TipoMedidaEnum.pm10, TipoMedidaEnum.no2, TipoMedidaEnum.o3]

    def __init__(self):
        pass

    # ---------------------------------------------------------
    def get_aqi(self, tipo: TipoMedidaEnum, value: float) -> float:
        """
        Calcula el AQI basado en el tipo y valor de la medida.

        Args:
            tipo (TipoMedidaEnum): Tipo de medida (pm2_5, pm10, no2, o3).
            value (float): Valor de la medida.

        Returns:
            float: Valor de AQI calculado.
        """
        if value < 0:
            return 0.0

        if tipo == TipoMedidaEnum.pm2_5:
            breakpoints = [
                (0.0, 9.0, 0, 50),
                (9.1, 35.4, 51, 100),
                (35.5, 55.4, 101, 150),
                (55.5, 125.4, 151, 200),
                (125.5, 225.4, 201, 300),
                (225.5, 325.4, 301, 400),
                (325.5, 605.4, 401, 500),
            ]
            if value > 605.4:
                return 500 + ((value - 605.4) / 280.0) * 100
            for c_lo, c_hi, i_lo, i_hi in breakpoints:
                if c_lo <= value <= c_hi:
                    return ((i_hi - i_lo) / (c_hi - c_lo)) * (value - c_lo) + i_lo

        elif tipo == TipoMedidaEnum.pm10:
            breakpoints = [
                (0.0, 54.0, 0, 50),
                (55.0, 154.0, 51, 100),
                (155.0, 254.0, 101, 150),
                (255.0, 354.0, 151, 200),
                (355.0, 424.0, 201, 300),
                (425.0, 504.0, 301, 400),
                (505.0, 604.0, 401, 500),
            ]
            if value > 604.0:
                return 500 + ((value - 604.0) / 100.0) * 100
            for c_lo, c_hi, i_lo, i_hi in breakpoints:
                if c_lo <= value <= c_hi:
                    return ((i_hi - i_lo) / (c_hi - c_lo)) * (value - c_lo) + i_lo

        elif tipo == TipoMedidaEnum.no2:
            breakpoints = [
                (0.0, 53.0, 0, 50),
                (54.0, 100.0, 51, 100),
                (101.0, 360.0, 101, 150),
                (361.0, 649.0, 151, 200),
                (650.0, 1249.0, 201, 300),
                (1250.0, 1649.0, 301, 400),
                (1650.0, 2049.0, 401, 500),
            ]
            if value > 2049.0:
                return 500 + ((value - 2049.0) / 400.0) * 100
            for c_lo, c_hi, i_lo, i_hi in breakpoints:
                if c_lo <= value <= c_hi:
                    return ((i_hi - i_lo) / (c_hi - c_lo)) * (value - c_lo) + i_lo

        elif tipo == TipoMedidaEnum.o3:
            breakpoints = [
                (0.0, 0.054, 0, 50),
                (0.055, 0.070, 51, 100),
                (0.071, 0.085, 101, 150),
                (0.086, 0.105, 151, 200),
                (0.106, 0.200, 201, 300),
            ]
            if value > 0.200:
                return 300 + ((value - 0.200) / 0.1) * 100
            for c_lo, c_hi, i_lo, i_hi in breakpoints:
                if c_lo <= value <= c_hi:
                    return ((i_hi - i_lo) / (c_hi - c_lo)) * (value - c_lo) + i_lo

        return 0.0

    # ---------------------------------------------------------
    def get_color_from_aqi(self, aqi: float) -> str:
        """
        Obtiene el color basado en el valor de AQI.

        Args:
            aqi (float): Valor de AQI.

        Returns:
            str: Color correspondiente ("verde", "amarillo", "rojo").
        """
        if aqi <= 50:
            return "verde"
        elif aqi <= 100:
            return "amarillo"
        else:
            return "rojo"

    # ---------------------------------------------------------
    def obtener_mapa_de_tipo_de_dia_de_destino(self, db: Session, tipo: str, fecha: datetime, esquina_inf_izq: PosicionGPS, esquina_sup_der: PosicionGPS) -> Dict:
        """
        Obtiene el mapa para un tipo y día, dentro de bounds. Para cada hora, recolecta todas las medidas hasta esa hora inclusive, y toma la más reciente por ubicación.

        Args:
            db (Session): Sesión de base de datos.
            tipo (str): Tipo de medida o "general".
            fecha (datetime): Fecha para obtener los datos.
            esquina_inf_izq (PosicionGPS): Esquina inferior izquierda del bounding box.
            esquina_sup_der (PosicionGPS): Esquina superior derecha del bounding box.

        Returns:
            Dict: Datos del mapa organizados por hora.
        """
        response = {"data": {}}
        if tipo == "general":
            # Consulta calidad_general en lugar de medidas
            query = db.query(CalidadGeneral).filter(
                CalidadGeneral.fecha_hora >= fecha.replace(hour=0, minute=0),
                CalidadGeneral.fecha_hora < fecha + timedelta(days=1),
                CalidadGeneral.lat >= esquina_inf_izq.lat,
                CalidadGeneral.lat <= esquina_sup_der.lat,
                CalidadGeneral.lon >= esquina_inf_izq.lon,
                CalidadGeneral.lon <= esquina_sup_der.lon
            )
            results = query.all()
            
            # Si no hay resultados, calculamos bajo demanda y volvemos a consultar
            if not results:
                print(f"No hay datos de calidad general para {fecha.date()}. Calculando bajo demanda...")
                unified = self.unificar_medidas_de_todos_tipos_de_dia(db, fecha, esquina_inf_izq, esquina_sup_der)
                self.calcular_calidad_general_del_aire(db, unified, fecha)
                results = query.all() # Re-query

            for r in results:
                hour = r.fecha_hora.hour
                if hour not in response["data"]:
                    response["data"][hour] = []
                response["data"][hour].append({
                    "lat": r.lat,
                    "lng": r.lon,
                    "value": r.valor,
                    "color": r.color  # Usa el color precalculado
                })
            return response
        else:
            # Código existente para gases específicos (mantén lo que ya tienes aquí, solo añade el if para general)
            medidas = self.obtener_medidas_tipo_fecha_sitio(db, TipoMedidaEnum[tipo], fecha, esquina_inf_izq, esquina_sup_der, False)
            interpoladas = self.obtener_medidas_tipo_fecha_sitio(db, TipoMedidaEnum[tipo], fecha, esquina_inf_izq, esquina_sup_der, True)
            all_medidas = medidas + interpoladas
            for m in all_medidas:
                hour = m.fecha_hora.hour
                if hour not in response["data"]:
                    response["data"][hour] = []
                aqi = self.get_aqi(TipoMedidaEnum[tipo], m.valor)
                color = self.get_color_from_aqi(aqi)
                response["data"][hour].append({
                    "lat": m.posicion.lat,
                    "lng": m.posicion.lon,
                    "value": m.valor,
                    "color": color
                })
            return response

    # ---------------------------------------------------------
    def obtener_medidas_tipo_fecha_sitio(self, db: Session, tipo: TipoMedidaEnum, fecha: datetime, esquina_inf_izq: PosicionGPS, esquina_sup_der: PosicionGPS, interpoladas: bool = False) -> List[Medida]:
        """
        Obtiene medidas de un tipo, fecha y sitio, reales o interpoladas.

        Args:
            db (Session): Sesión de base de datos.
            tipo (TipoMedidaEnum): Tipo de medida.
            fecha (datetime): Fecha para obtener los datos.
            esquina_inf_izq (PosicionGPS): Esquina inferior izquierda del bounding box.
            esquina_sup_der (PosicionGPS): Esquina superior derecha del bounding box.
            interpoladas (bool): Si se deben obtener interpoladas (default False).

        Returns:
            List[Medida]: Lista de medidas.
        """
        start = fecha.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        if not interpoladas:
            query = db.query(DBMedida).filter(
                DBMedida.tipo == tipo,
                DBMedida.fecha_hora >= start,
                DBMedida.fecha_hora < end,
                DBMedida.lat >= esquina_inf_izq.lat,
                DBMedida.lat <= esquina_sup_der.lat,
                DBMedida.lon >= esquina_inf_izq.lon,
                DBMedida.lon <= esquina_sup_der.lon
            ).all()
            return [Medida(None, None, q.tipo, q.valor, q.fecha_hora, PosicionGPS(q.lat, q.lon)) for q in query]
        else:
            query = db.query(DBInterpolada).filter(
                DBInterpolada.tipo == tipo,
                DBInterpolada.fecha_hora >= start,
                DBInterpolada.fecha_hora < end,
                DBInterpolada.lat >= esquina_inf_izq.lat,
                DBInterpolada.lat <= esquina_sup_der.lat,
                DBInterpolada.lon >= esquina_inf_izq.lon,
                DBInterpolada.lon <= esquina_sup_der.lon
            ).all()
            return [Medida(None, None, q.tipo, q.valor, q.fecha_hora, PosicionGPS(q.lat, q.lon)) for q in query]

    # ---------------------------------------------------------
    def construir_matriz_interpolacion(self, esquina_inf_izq: PosicionGPS, esquina_sup_der: PosicionGPS) -> List[PosicionGPS]:
        """
        Construye una lista de puntos de grilla para interpolación.

        Args:
            esquina_inf_izq (PosicionGPS): Esquina inferior izquierda del bounding box.
            esquina_sup_der (PosicionGPS): Esquina superior derecha del bounding box.

        Returns:
            List[PosicionGPS]: Lista de puntos en la grilla.
        """
        delta_lat = 0.0009  # ~100m
        delta_lon = 0.00114  # ~100m at 39N
        points = []
        lat = esquina_inf_izq.lat
        while lat <= esquina_sup_der.lat:
            lon = esquina_inf_izq.lon
            while lon <= esquina_sup_der.lon:
                points.append(PosicionGPS(lat, lon))
                lon += delta_lon
            lat += delta_lat
        return points

    # ---------------------------------------------------------
    def interpolar_para_punto(self, punto: PosicionGPS, medidas: List[Medida]) -> float:
        """
        Interpola el valor para un punto usando IDW (Inverse Distance Weighting).

        Args:
            punto (PosicionGPS): Punto para interpolar.
            medidas (List[Medida]): Lista de medidas cercanas.

        Returns:
            float: Valor interpolado.
        """
        if not medidas:
            return 0.0
        weights_sum = 0.0
        weighted_val = 0.0
        for m in medidas:
            dist = PosicionGPS.distancia_entre_dos(punto, m.posicion)
            if dist < 1e-6:
                return m.valor
            if dist > 0:
                weight = 1 / (dist ** 2)
                weighted_val += m.valor * weight
                weights_sum += weight
        if weights_sum == 0:
            return 0.0
        return weighted_val / weights_sum

    # ---------------------------------------------------------
    def interpolar_para_tipo_fecha(self, db: Session, tipo: TipoMedidaEnum, fecha: datetime, esquina_inf_izq: PosicionGPS, esquina_sup_der: PosicionGPS) -> str:
        """
        Realiza interpolación para un tipo y fecha, almacena en DB. Interpolaciones por hora.

        Args:
            db (Session): Sesión de base de datos.
            tipo (TipoMedidaEnum): Tipo de medida.
            fecha (datetime): Fecha para interpolar.
            esquina_inf_izq (PosicionGPS): Esquina inferior izquierda del bounding box.
            esquina_sup_der (PosicionGPS): Esquina superior derecha del bounding box.

        Returns:
            str: "OK" si exitoso, mensaje de error si no.
        """
        try:
            grid_points = self.construir_matriz_interpolacion(esquina_inf_izq, esquina_sup_der)
            for h in range(24):
                end_h = fecha.replace(hour=h, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
                real_medidas_h = self.obtener_medidas_tipo_fecha_sitio(db, tipo, fecha, esquina_inf_izq, esquina_sup_der, False)
                medidas_until_h = [m for m in real_medidas_h if m.fecha_hora <= end_h]
                if not medidas_until_h:
                    continue
                for punto in grid_points:
                    min_dist = min(PosicionGPS.distancia_entre_dos(punto, m.posicion) for m in medidas_until_h) if medidas_until_h else inf
                    if min_dist < 50:
                        continue
                    valor = self.interpolar_para_punto(punto, medidas_until_h)
                    fh = fecha.replace(hour=h, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
                    interp = DBInterpolada(
                        lectura_id=str(uuid.uuid4()),
                        fecha_hora=fh,
                        tipo=tipo,
                        lat=punto.lat,
                        lon=punto.lon,
                        valor=valor
                    )
                    db.add(interp)
            db.commit()
            return "OK"
        except Exception as e:
            db.rollback()
            return f"Error: {str(e)}"

    # ---------------------------------------------------------
    def unificar_medidas_de_todos_tipos_de_dia(self, db: Session, fecha: datetime, esquina_inf_izq, esquina_sup_der):
        """
        Unifica medidas de todos los tipos para un día (ambas tablas). Acumulativo hasta cada hora.

        Args:
            db (Session): Sesión de base de datos.
            fecha (datetime): Fecha para unificar.
            esquina_inf_izq (PosicionGPS): Esquina inferior izquierda del bounding box.
            esquina_sup_der (PosicionGPS): Esquina superior derecha del bounding box.

        Returns:
            Dict: Medidas unificadas por hora y posición.
        """
        unified = {}

        for t in self.GASES:
            for h in range(24):
                start_h = fecha.replace(hour=h, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
                end_h   = fecha.replace(hour=h, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)

                # Solo medidas de ESTA HORA (mucho más rápido)
                reales = db.query(DBMedida).filter(
                    DBMedida.tipo == t,
                    DBMedida.fecha_hora >= start_h,
                    DBMedida.fecha_hora <= end_h,
                    DBMedida.lat >= esquina_inf_izq.lat,
                    DBMedida.lat <= esquina_sup_der.lat,
                    DBMedida.lon >= esquina_inf_izq.lon,
                    DBMedida.lon <= esquina_sup_der.lon
                ).all()

                interps = db.query(DBInterpolada).filter(
                    DBInterpolada.tipo == t,
                    DBInterpolada.fecha_hora >= start_h,
                    DBInterpolada.fecha_hora <= end_h,
                    DBInterpolada.lat >= esquina_inf_izq.lat,
                    DBInterpolada.lat <= esquina_sup_der.lat,
                    DBInterpolada.lon >= esquina_inf_izq.lon,
                    DBInterpolada.lon <= esquina_sup_der.lon
                ).all()

                # Elegimos siempre la última medida por posición
                all_h = reales + interps
                latest_by_pos = {}
                for m in sorted(all_h, key=lambda x: x.fecha_hora):
                    key = f"{m.lat}_{m.lon}"
                    latest_by_pos[key] = m.valor

                for key, valor in latest_by_pos.items():
                    lat, lon = map(float, key.split('_'))
                    index = f"{h}_{key}"
                    if index not in unified:
                        unified[index] = {}
                    unified[index][t.name] = valor

        return unified

    # ---------------------------------------------------------
    def calcular_calidad_general_del_aire(self, db: Session, medidas_json: Dict, fecha: datetime):
        """
        Calcula la calidad general del aire y almacena en DB. Usa unificado acumulativo.

        Args:
            db (Session): Sesión de base de datos.
            medidas_json (Dict): Medidas unificadas.
            fecha (datetime): Fecha para calcular.

        Returns:
            str: "OK" si exitoso, mensaje de error si no.
        """
        try:
            for key, vals in medidas_json.items():
                h, lat, lon = key.split('_')
                h = int(h)
                lat = float(lat)
                lon = float(lon)

                # Sacar AQI por contaminante
                aqis = []
                for t_name, value in vals.items():
                    t = TipoMedidaEnum[t_name]
                    aqis.append(self.get_aqi(t, value))

                if not aqis:
                    continue

                max_aqi = max(aqis)
                color = self.get_color_from_aqi(max_aqi)

                fh = fecha.replace(hour=h, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

                entry = CalidadGeneral(
                    valor_id=str(uuid.uuid4()),
                    valor=max_aqi,
                    color=color,
                    fecha_hora=fh,
                    lat=lat,
                    lon=lon
                )
                db.add(entry)

            db.commit()
            return "OK"

        except Exception as e:
            db.rollback()
            return f"Error: {str(e)}"

# ---------------------------------------------------------
