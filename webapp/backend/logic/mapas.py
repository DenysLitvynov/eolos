# File: backend/logic/mapas.py (MODIFICADO)
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
    # Función auxiliar para calcular AQI basado en el tipo y valor
    # ---------------------------------------------------------
    def get_aqi(self, tipo: TipoMedidaEnum, value: float) -> float:
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
    # Función auxiliar para obtener color basado en AQI
    # ---------------------------------------------------------
    def get_color_from_aqi(self, aqi: float) -> str:
        if aqi <= 50:
            return "verde"
        elif aqi <= 100:
            return "amarillo"
        else:
            return "rojo"

    # ---------------------------------------------------------
    # Obtiene el mapa para un tipo y día, dentro de bounds - MODIFICADO para acumulativo
    # Para cada hora, recolecta todas las medidas hasta esa hora inclusive, y toma la más reciente por ubicación
    # ---------------------------------------------------------
    # File: backend/logic/mapas.py → método obtener_mapa_de_tipo_de_dia_de_destino

    # File: backend/logic/mapas.py → método obtener_mapa_de_tipo_de_dia_de_destino

    def obtener_mapa_de_tipo_de_dia_de_destino(self, db: Session, tipo: str, fecha: datetime, esquina_inf_izq: PosicionGPS, esquina_sup_der: PosicionGPS) -> Dict:
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

    # Obtiene medidas de tipo/fecha/sitio, reales o interpoladas - Sin cambios
    # ---------------------------------------------------------
    def obtener_medidas_tipo_fecha_sitio(self, db: Session, tipo: TipoMedidaEnum, fecha: datetime, esquina_inf_izq: PosicionGPS, esquina_sup_der: PosicionGPS, interpoladas: bool = False) -> List[Medida]:
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
    # Construye lista de puntos de grilla para interpolación - Sin cambios
    # ---------------------------------------------------------
    def construir_matriz_interpolacion(self, esquina_inf_izq: PosicionGPS, esquina_sup_der: PosicionGPS) -> List[PosicionGPS]:
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
    # Interpola valor para un punto usando IDW - Sin cambios
    # ---------------------------------------------------------
    def interpolar_para_punto(self, punto: PosicionGPS, medidas: List[Medida]) -> float:
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
    # Realiza interpolación para tipo/fecha, almacena en DB - MODIFICADO para interpolaciones por hora
    # ---------------------------------------------------------
    def interpolar_para_tipo_fecha(self, db: Session, tipo: TipoMedidaEnum, fecha: datetime, esquina_inf_izq: PosicionGPS, esquina_sup_der: PosicionGPS) -> str:
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
    # Unifica medidas de todos tipos para un día (ambas tablas) - MODIFICADO para acumulativo hasta cada hora
    # ---------------------------------------------------------
    def unificar_medidas_de_todos_tipos_de_dia(self, db: Session, fecha: datetime, esquina_inf_izq: PosicionGPS, esquina_sup_der: PosicionGPS) -> Dict:
        unified: Dict[str, Dict] = {}
        for t in self.GASES:
            for h in range(24):
                end_h = fecha.replace(hour=h, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
                medidas = self.obtener_medidas_tipo_fecha_sitio(db, t, fecha, esquina_inf_izq, esquina_sup_der, False)
                interps = self.obtener_medidas_tipo_fecha_sitio(db, t, fecha, esquina_inf_izq, esquina_sup_der, True)
                all_m_until_h = [m for m in (medidas + interps) if m.fecha_hora <= end_h]
                
                # Tomar última por ubicación
                latest_by_pos = {}
                for m in sorted(all_m_until_h, key=lambda x: x.fecha_hora):
                    key_pos = f"{m.posicion.lat}_{m.posicion.lon}"
                    latest_by_pos[key_pos] = m.valor
                
                for key_pos, valor in latest_by_pos.items():
                    lat, lon = map(float, key_pos.split('_'))
                    key = f"{h}_{lat}_{lon}"
                    if key not in unified:
                        unified[key] = {}
                    unified[key][t.name] = valor
        return unified

    # ---------------------------------------------------------
    # Calcula calidad general y almacena en DB - Sin cambios mayores, pero usa unificado acumulativo
    # ---------------------------------------------------------
    def calcular_calidad_general_del_aire(self, db: Session, medidas_json: Dict, fecha: datetime) -> str:
        try:
            # 0. Check if data already exists for this day
            start_day = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
            end_day = start_day + timedelta(days=1)
            
            exists = db.query(CalidadGeneral).filter(
                CalidadGeneral.fecha_hora >= start_day,
                CalidadGeneral.fecha_hora < end_day
            ).first()
            
            if exists:
                print(f"Calidad general para {start_day.date()} ya existe. No se recalcula.")
                return "OK"

            for key, vals in medidas_json.items():
                parts = key.split('_')
                if len(parts) != 3:
                    continue
                h, lat_str, lon_str = parts
                h = int(h)
                lat = float(lat_str)
                lon = float(lon_str)
                aqis = []
                for t_name, val in vals.items():
                    t = TipoMedidaEnum[t_name]
                    aqi = self.get_aqi(t, val)
                    aqis.append(aqi)
                if not aqis:
                    continue
                max_aqi = max(aqis)
                color = self.get_color_from_aqi(max_aqi)
                fh = fecha.replace(hour=h, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
                cg = CalidadGeneral(
                    valor_id=str(uuid.uuid4()),
                    valor=max_aqi,
                    color=color,
                    fecha_hora=fh,
                    lat=lat,
                    lon=lon
                )
                db.add(cg)
            db.commit()
            return "OK"
        except Exception as e:
            db.rollback()
            return f"Error: {str(e)}"

# ---------------------------------------------------------
