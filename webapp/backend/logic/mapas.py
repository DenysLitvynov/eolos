"""
Autor: Denys Litvynov Lymanets
Fecha: 04-12-2025
Descripción: Lógica de negocio para mapas de calidad del aire.
Optimizado para rendimiento y visualización.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
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
    
    # Área reducida por defecto para mejorar rendimiento
    AREA_LIMITADA = True
    LAT_MIN_LIMIT = 39.44
    LAT_MAX_LIMIT = 39.50
    LON_MIN_LIMIT = -0.42
    LON_MAX_LIMIT = -0.34
    
    def __init__(self):
        # Cache para evitar cálculos repetidos
        self._cache_interpolaciones = {}
        self._cache_general = {}
        print("LogicaMapas inicializado con optimizaciones de rendimiento")

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
    def obtener_mapa_de_tipo_de_dia_de_destino(self, db: Session, tipo: str, fecha: datetime, 
                                             esquina_inf_izq: PosicionGPS, esquina_sup_der: PosicionGPS) -> Dict:
        """
        Obtiene el mapa para un tipo y día, dentro de bounds. Para cada hora, recolecta todas 
        las medidas hasta esa hora inclusive, y toma la más reciente por ubicación.
        CON CACHÉ para mejorar rendimiento.
        """
        # Clave de caché única por consulta
        cache_key = f"{tipo}_{fecha.date()}_{esquina_inf_izq.lat:.4f}_{esquina_inf_izq.lon:.4f}"
        
        if cache_key in self._cache_general:
            print(f"✓ Usando caché para {cache_key}")
            return self._cache_general[cache_key]
        
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
            
            # Si no hay resultados, calculamos bajo demanda
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
                    "color": r.color
                })
            
            # Almacenar en caché (limitar tamaño)
            if len(self._cache_general) > 50:
                self._cache_general.clear()
            
            self._cache_general[cache_key] = response
            return response
        else:
            # PARA GASES ESPECÍFICOS: asegurar que hay interpolaciones
            tipo_enum = TipoMedidaEnum[tipo]
            
            # Verificar si hay suficientes medidas para este día/área
            medidas_reales = self.obtener_medidas_tipo_fecha_sitio(db, tipo_enum, fecha, esquina_inf_izq, esquina_sup_der, False)
            medidas_interpoladas = self.obtener_medidas_tipo_fecha_sitio(db, tipo_enum, fecha, esquina_inf_izq, esquina_sup_der, True)
            
            # Si no hay suficientes datos interpolados, calcularlos bajo demanda
            # PERO con límite: máximo 200 puntos interpolados por hora
            if len(medidas_interpoladas) < 50 and len(medidas_reales) > 5:
                print(f"Calculando interpolaciones limitadas para {tipo} en {fecha.date()} bajo demanda...")
                self.interpolar_para_tipo_fecha(db, tipo_enum, fecha, esquina_inf_izq, esquina_sup_der)
                # Re-obtener interpoladas después de calcular
                medidas_interpoladas = self.obtener_medidas_tipo_fecha_sitio(db, tipo_enum, fecha, esquina_inf_izq, esquina_sup_der, True)
            
            all_medidas = medidas_reales + medidas_interpoladas
            
            # LIMITAR: Tomar máximo 300 puntos por hora para mejorar rendimiento
            if len(all_medidas) > 300:
                all_medidas = all_medidas[:300]
                print(f"Limitando a {len(all_medidas)} puntos para mejorar rendimiento")
            
            # Agrupar por ubicación y hora, tomando la más reciente
            medidas_por_hora = {}
            for m in all_medidas:
                hour = m.fecha_hora.hour
                key = f"{hour}_{m.posicion.lat:.6f}_{m.posicion.lon:.6f}"
                
                # Si ya existe, mantener la más reciente
                if key in medidas_por_hora:
                    if m.fecha_hora > medidas_por_hora[key].fecha_hora:
                        medidas_por_hora[key] = m
                else:
                    medidas_por_hora[key] = m
            
            # Construir respuesta
            for key, m in medidas_por_hora.items():
                hour = int(key.split('_')[0])
                if hour not in response["data"]:
                    response["data"][hour] = []
                
                aqi = self.get_aqi(tipo_enum, m.valor)
                color = self.get_color_from_aqi(aqi)
                
                response["data"][hour].append({
                    "lat": m.posicion.lat,
                    "lng": m.posicion.lon,
                    "value": m.valor,
                    "color": color
                })
            
            # Almacenar en caché (limitar tamaño)
            if len(self._cache_general) > 50:
                self._cache_general.clear()
            
            self._cache_general[cache_key] = response
            return response

    # ---------------------------------------------------------
    def obtener_medidas_tipo_fecha_sitio(self, db: Session, tipo: TipoMedidaEnum, fecha: datetime, 
                                       esquina_inf_izq: PosicionGPS, esquina_sup_der: PosicionGPS, 
                                       interpoladas: bool = False) -> List[Medida]:
        """
        Obtiene medidas de un tipo, fecha y sitio, reales o interpoladas.
        CON ÁREA LIMITADA para mejorar rendimiento.
        """
        # APLICAR LÍMITES DE ÁREA si está activado
        if self.AREA_LIMITADA:
            lat_min = max(self.LAT_MIN_LIMIT, esquina_inf_izq.lat)
            lat_max = min(self.LAT_MAX_LIMIT, esquina_sup_der.lat)
            lon_min = max(self.LON_MIN_LIMIT, esquina_inf_izq.lon)
            lon_max = min(self.LON_MAX_LIMIT, esquina_sup_der.lon)
            
            # Verificar si el área solicitada está fuera de los límites
            if lat_min > lat_max or lon_min > lon_max:
                print(f"Área solicitada fuera de límites: {esquina_inf_izq} -> {esquina_sup_der}")
                return []
        else:
            lat_min = esquina_inf_izq.lat
            lat_max = esquina_sup_der.lat
            lon_min = esquina_inf_izq.lon
            lon_max = esquina_sup_der.lon
        
        start = fecha.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        
        if not interpoladas:
            query = db.query(DBMedida).filter(
                DBMedida.tipo == tipo,
                DBMedida.fecha_hora >= start,
                DBMedida.fecha_hora < end,
                DBMedida.lat >= lat_min,
                DBMedida.lat <= lat_max,
                DBMedida.lon >= lon_min,
                DBMedida.lon <= lon_max
            ).limit(1000).all()  # LIMIT para mejorar rendimiento
            return [Medida(None, None, q.tipo, q.valor, q.fecha_hora, PosicionGPS(q.lat, q.lon)) for q in query]
        else:
            query = db.query(DBInterpolada).filter(
                DBInterpolada.tipo == tipo,
                DBInterpolada.fecha_hora >= start,
                DBInterpolada.fecha_hora < end,
                DBInterpolada.lat >= lat_min,
                DBInterpolada.lat <= lat_max,
                DBInterpolada.lon >= lon_min,
                DBInterpolada.lon <= lon_max
            ).limit(1000).all()  # LIMIT para mejorar rendimiento
            return [Medida(None, None, q.tipo, q.valor, q.fecha_hora, PosicionGPS(q.lat, q.lon)) for q in query]

    # ---------------------------------------------------------
    def construir_matriz_interpolacion(self, esquina_inf_izq: PosicionGPS, esquina_sup_der: PosicionGPS) -> List[PosicionGPS]:
        """
        Construye una lista de puntos de grilla para interpolación.
        OPTIMIZADO: Menos puntos y más espaciados para mejor rendimiento.
        """
        # INCREMENTAR ESPACIADO: de ~100m a ~300m para menos puntos
        delta_lat = 0.0027  # ~300m (antes 0.0009)
        delta_lon = 0.00342  # ~300m at 39N (antes 0.00114)
        
        # LIMITAR MÁXIMO DE PUNTOS
        max_puntos = 300  # Antes ilimitado (~1500+ puntos)
        points = []
        
        lat = esquina_inf_izq.lat
        puntos_count = 0
        
        while lat <= esquina_sup_der.lat and puntos_count < max_puntos:
            lon = esquina_inf_izq.lon
            while lon <= esquina_sup_der.lon and puntos_count < max_puntos:
                points.append(PosicionGPS(lat, lon))
                puntos_count += 1
                lon += delta_lon
            lat += delta_lat
        
        print(f"✓ Puntos de interpolación generados: {len(points)} (antes ~1500+)")
        return points

    # ---------------------------------------------------------
    def interpolar_para_punto(self, punto: PosicionGPS, medidas: List[Medida]) -> float:
        """
        Interpola el valor para un punto usando IDW (Inverse Distance Weighting).
        OPTIMIZADO: Usar menos medidas cercanas.
        """
        if not medidas:
            return 0.0
        
        # LIMITAR a solo las 10 medidas más cercanas para mejor rendimiento
        medidas_con_distancia = []
        for m in medidas:
            dist = PosicionGPS.distancia_entre_dos(punto, m.posicion)
            if dist < 1e-6:
                return m.valor
            medidas_con_distancia.append((dist, m))
        
        # Ordenar por distancia y tomar las 10 más cercanas
        medidas_con_distancia.sort(key=lambda x: x[0])
        medidas_limitadas = [m for _, m in medidas_con_distancia[:10]]
        
        weights_sum = 0.0
        weighted_val = 0.0
        for m in medidas_limitadas:
            dist = PosicionGPS.distancia_entre_dos(punto, m.posicion)
            if dist > 0:
                weight = 1 / (dist ** 2)
                weighted_val += m.valor * weight
                weights_sum += weight
        
        if weights_sum == 0:
            return 0.0
        return weighted_val / weights_sum

    # ---------------------------------------------------------
    def interpolar_para_tipo_fecha(self, db: Session, tipo: TipoMedidaEnum, fecha: datetime, 
                                 esquina_inf_izq: PosicionGPS, esquina_sup_der: PosicionGPS) -> str:
        """
        Realiza interpolación para un tipo y fecha, almacena en DB.
        OPTIMIZADO: Menos puntos y por horas clave.
        """
        try:
            grid_points = self.construir_matriz_interpolacion(esquina_inf_izq, esquina_sup_der)
            
            # Solo interpolar para horas clave (no todas las 24)
            horas_clave = [8, 12, 16, 20]  # Horas de más tráfico/actividad
            
            for h in horas_clave:
                end_h = fecha.replace(hour=h, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
                real_medidas_h = self.obtener_medidas_tipo_fecha_sitio(db, tipo, fecha, esquina_inf_izq, esquina_sup_der, False)
                medidas_until_h = [m for m in real_medidas_h if m.fecha_hora <= end_h]
                
                if not medidas_until_h:
                    continue
                
                # LIMITAR: Solo interpolar cada 2º punto de la grilla
                for i, punto in enumerate(grid_points):
                    if i % 2 != 0:  # Saltar puntos impares
                        continue
                    
                    min_dist = min(PosicionGPS.distancia_entre_dos(punto, m.posicion) for m in medidas_until_h) if medidas_until_h else inf
                    if min_dist < 100:  # 100 metros (antes 50)
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
            print(f"✓ Interpolaciones creadas para {tipo} en {fecha.date()}")
            return "OK"
        except Exception as e:
            db.rollback()
            print(f"✗ Error en interpolación: {str(e)}")
            return f"Error: {str(e)}"

    # ---------------------------------------------------------
    def unificar_medidas_de_todos_tipos_de_dia(self, db: Session, fecha: datetime, esquina_inf_izq, esquina_sup_der):
        """
        Unifica medidas de todos los tipos para un día (ambas tablas).
        OPTIMIZADO: Solo horas clave.
        """
        unified = {}
        
        # Solo procesar horas clave para mejor rendimiento
        horas_clave = list(range(24))  # Podríamos reducir a [8, 12, 16, 20] si es necesario
        
        for t in self.GASES:
            for h in horas_clave:
                start_h = fecha.replace(hour=h, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
                end_h   = fecha.replace(hour=h, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)

                # Solo medidas de ESTA HORA
                reales = db.query(DBMedida).filter(
                    DBMedida.tipo == t,
                    DBMedida.fecha_hora >= start_h,
                    DBMedida.fecha_hora <= end_h,
                    DBMedida.lat >= esquina_inf_izq.lat,
                    DBMedida.lat <= esquina_sup_der.lat,
                    DBMedida.lon >= esquina_inf_izq.lon,
                    DBMedida.lon <= esquina_sup_der.lon
                ).limit(200).all()  # LIMIT

                interps = db.query(DBInterpolada).filter(
                    DBInterpolada.tipo == t,
                    DBInterpolada.fecha_hora >= start_h,
                    DBInterpolada.fecha_hora <= end_h,
                    DBInterpolada.lat >= esquina_inf_izq.lat,
                    DBInterpolada.lat <= esquina_sup_der.lat,
                    DBInterpolada.lon >= esquina_inf_izq.lon,
                    DBInterpolada.lon <= esquina_sup_der.lon
                ).limit(200).all()  # LIMIT

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

        print(f"✓ Medidas unificadas: {len(unified)} puntos")
        return unified

    # ---------------------------------------------------------
    def calcular_calidad_general_del_aire(self, db: Session, medidas_json: Dict, fecha: datetime):
        """
        Calcula la calidad general del aire y almacena en DB.
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
            print(f"✓ Calidad general calculada y almacenada")
            return "OK"

        except Exception as e:
            db.rollback()
            print(f"✗ Error calculando calidad general: {str(e)}")
            return f"Error: {str(e)}"

# ---------------------------------------------------------
