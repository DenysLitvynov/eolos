"""
Autor: JINWEI
Fecha: 21-12-2025

Descripción: lógica Home + KM resumen:
- km acumulados desde recompensas_usuario
- descuento desde recompensas_obtenidas + recompensas.descripcion
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from ..db.models import Usuario, Trayecto, Medida, CalidadGeneral, PlacaSensores
from ..logic.km_logic import LogicaKm


class LogicaHome:
    def __init__(self):
        self.km_logic = LogicaKm()

    def _clamp_score(self, v):
        if v is None:
            return None
        try:
            return int(round(float(v)))
        except Exception:
            return None

    def _map_estado(self, color: str | None):
        if not color:
            return ("Mala", "No hay datos recientes de calidad del aire.")
        c = color.strip().lower()
        if c == "verde":
            return ("Buena", "La calidad del aire es satisfactoria y la contaminación del aire presenta poco o ningún riesgo.")
        if c == "amarillo":
            return ("Mala", "El aire ha alcanzado un nivel de contaminación moderado. Algunas personas pueden experimentar molestias.")
        if c == "rojo":
            return ("Poco Saludable", "La calidad del aire es deficiente y puede suponer un riesgo para la salud.")
        return ("Mala", "No hay datos recientes de calidad del aire.")

    def _get_ultimo_trayecto(self, db: Session, usuario_id: str):
        return (
            db.query(Trayecto)
            .filter(Trayecto.usuario_id == usuario_id)
            .order_by(desc(func.coalesce(Trayecto.fecha_fin, Trayecto.fecha_inicio)))
            .first()
        )

    def _get_placa_id_by_bicicleta(self, db: Session, bicicleta_id: str | None):
        if not bicicleta_id:
            return None
        ps = (
            db.query(PlacaSensores)
            .filter(PlacaSensores.bicicleta_id == bicicleta_id)
            .first()
        )
        return str(ps.placa_id) if ps else None

    def _get_latest_gases_by_placa(self, db: Session, placa_id: str):
        sub = (
            db.query(
                Medida.tipo.label("tipo"),
                func.max(Medida.fecha_hora).label("max_fecha"),
            )
            .filter(Medida.placa_id == placa_id)
            .group_by(Medida.tipo)
            .subquery()
        )

        rows = (
            db.query(Medida)
            .join(sub, (Medida.tipo == sub.c.tipo) & (Medida.fecha_hora == sub.c.max_fecha))
            .filter(Medida.placa_id == placa_id)
            .order_by(Medida.tipo.asc())
            .all()
        )

        gases = []
        for r in rows:
            tipo = r.tipo.value if hasattr(r.tipo, "value") else str(r.tipo)
            gases.append({"tipo": tipo, "valor": float(r.valor) if r.valor is not None else None})
        return gases

    def _get_latest_location_by_placa(self, db: Session, placa_id: str):
        m = (
            db.query(Medida)
            .filter(Medida.placa_id == placa_id)
            .order_by(desc(Medida.fecha_hora))
            .first()
        )
        if m:
            return float(m.lat), float(m.lon)
        return None

    def _get_calidad_by_location(self, db: Session, lat: float, lon: float):
        dist2 = (
            (CalidadGeneral.lat - lat) * (CalidadGeneral.lat - lat) +
            (CalidadGeneral.lon - lon) * (CalidadGeneral.lon - lon)
        )
        return (
            db.query(CalidadGeneral)
            .order_by(dist2.asc(), desc(CalidadGeneral.fecha_hora))
            .first()
        )

    def obtener_home(self, db: Session, usuario_id: str, lat: float | None = None, lon: float | None = None):
        user = db.query(Usuario).filter(Usuario.usuario_id == usuario_id).first()
        nombre_visible = ((user.nombre or "").strip() if user else "Usuario")

        ultimo = self._get_ultimo_trayecto(db, usuario_id)
        bicicleta_id = None
        ultimo_trayecto = None

        if ultimo:
            bicicleta_id = str(ultimo.bicicleta_id) if ultimo.bicicleta_id else None

            distancia_km = float(ultimo.distancia_total) if ultimo.distancia_total is not None else None

            tiempo_min = None
            if ultimo.fecha_inicio:
                fin = ultimo.fecha_fin or datetime.now(timezone.utc)
                delta = fin - ultimo.fecha_inicio
                tiempo_min = int(round(delta.total_seconds() / 60.0))

            ultimo_trayecto = {
                "trayecto_id": str(ultimo.trayecto_id),
                "bicicleta_id": bicicleta_id,
                "distancia_km": distancia_km,
                "tiempo_min": tiempo_min,
                "calidad_promedio": None,
            }

        placa_id = self._get_placa_id_by_bicicleta(db, bicicleta_id)

        if not placa_id:
            m_any = db.query(Medida).order_by(desc(Medida.fecha_hora)).first()
            placa_id = str(m_any.placa_id) if m_any else None

        gases = self._get_latest_gases_by_placa(db, placa_id) if placa_id else []
        nivel_actual = {"gases": gases}

        if (lat is None or lon is None) and placa_id:
            loc = self._get_latest_location_by_placa(db, placa_id)
            if loc:
                lat, lon = loc

        if lat is not None and lon is not None:
            cg = self._get_calidad_by_location(db, lat, lon)
        else:
            cg = db.query(CalidadGeneral).order_by(desc(CalidadGeneral.fecha_hora)).first()

        estado, descripcion = self._map_estado(cg.color if cg else None)
        score = self._clamp_score(cg.valor) if cg else None

        calidad_aire = {
            "score": score if score is not None else "--",
            "estado": estado,
            "descripcion": descripcion,
            "fecha_hora": cg.fecha_hora.isoformat() if cg and cg.fecha_hora else None,
            "lat": float(cg.lat) if cg else None,
            "lon": float(cg.lon) if cg else None,
        }

        if ultimo_trayecto:
            ultimo_trayecto["calidad_promedio"] = estado

        rutas = (
            db.query(func.count(Trayecto.trayecto_id))
            .filter(Trayecto.usuario_id == usuario_id)
            .scalar()
            or 0
        )

        impacto = {"rutas_limpias": int(rutas), "co2_kg": 0.0, "puntos": 0}

        # ✅ KM resumen（复用 km_logic）
        km, descuento = self.km_logic.obtener_resumen(db, usuario_id=usuario_id)
        base_price = 59.99
        usted_pagaria = max(base_price - descuento, 0.0)

        km_resumen = {
            "km_acumulados": float(km),
            "descuento_acumulado": float(descuento),
            "base_price": float(base_price),
            "usted_pagaria": float(usted_pagaria),
        }

        return {
            "usuario": {"usuario_id": usuario_id, "nombre_visible": nombre_visible},
            "placa_id": placa_id,
            "calidad_aire": calidad_aire,
            "nivel_actual": nivel_actual,
            "impacto": impacto,
            "ultimo_trayecto": ultimo_trayecto,
            "km_resumen": km_resumen,
        }
