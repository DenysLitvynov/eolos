"""
Autor: JINWEI
Fecha: 21-12-2025

Descripción general de la lógica Home:
- Último trayecto:
    * Información obtenida desde `trayectos`
    * Incluye distancia_total y duración (fecha_fin - fecha_inicio)
- placa_id:
    * Relación: trayectos.bicicleta_id → placas_sensores → placa_id
- gases:
    * Medidas asociadas a la placa_id
    * Se obtiene la última medición por cada tipo de gas (dinámico)
- calidad del aire:
    * Prioridad: GPS del cliente
    * Fallback: última ubicación registrada por la placa
    * Fuente: calidad_general (más cercana geográficamente)
- estado:
    * Estados normalizados para la UI:
      Buena / Mala / Poco Saludable (verde / amarillo / rojo)
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from ..db.models import Usuario, Trayecto, Medida, CalidadGeneral, PlacaSensores


class LogicaHome:
    """
    Clase que encapsula toda la lógica necesaria para construir
    la respuesta del endpoint Home del usuario.
    """

    def _clamp_score(self, v):
        """
        Normaliza el valor del índice de calidad del aire (AQI).
        - Redondea a entero
        - Devuelve None si el valor es inválido
        """
        if v is None:
            return None
        try:
            return int(round(float(v)))
        except Exception:
            return None


    # ✅ Unifica el estado de calidad del aire en 3 categorías
    def _map_estado(self, color: str | None):
        """
        Convierte el color almacenado en `calidad_general.color`
        a un estado textual y una descripción legible para la UI.
        """
        if not color:
            return (
                "Mala",
                "No hay datos recientes de calidad del aire."
            )

        c = color.strip().lower()

        # Colores habituales almacenados en la base de datos
        if c == "verde":
            return (
                "Buena",
                "La calidad del aire es satisfactoria y la contaminación del aire presenta poco o ningún riesgo."
            )
        if c == "amarillo":
            return (
                "Mala",
                "El aire ha alcanzado un nivel de contaminación moderado. Algunas personas pueden experimentar molestias."
            )
        if c == "rojo":
            return (
                "Poco Saludable",
                "La calidad del aire es deficiente y puede suponer un riesgo para la salud."
            )

        # Caso por defecto (fallback)
        return (
            "Mala",
            "No hay datos recientes de calidad del aire."
        )

    def _get_ultimo_trayecto(self, db: Session, usuario_id: str):
        """
        Obtiene el último trayecto del usuario ordenado por:
        - fecha_fin (si existe)
        - fecha_inicio (fallback)
        """
        return (
            db.query(Trayecto)
            .filter(Trayecto.usuario_id == usuario_id)
            .order_by(desc(func.coalesce(
                Trayecto.fecha_fin,
                Trayecto.fecha_inicio
            )))
            .first()
        )

    def _get_placa_id_by_bicicleta(self, db: Session, bicicleta_id: str | None):
        """
        Obtiene la placa asociada a una bicicleta.
        """
        if not bicicleta_id:
            return None

        ps = (
            db.query(PlacaSensores)
            .filter(PlacaSensores.bicicleta_id == bicicleta_id)
            .first()
        )

        return str(ps.placa_id) if ps else None

    def _get_latest_gases_by_placa(self, db: Session, placa_id: str):
        """
        Obtiene la última medición de cada tipo de gas
        para una placa concreta.
        """
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
            .join(
                sub,
                (Medida.tipo == sub.c.tipo) &
                (Medida.fecha_hora == sub.c.max_fecha)
            )
            .filter(Medida.placa_id == placa_id)
            .order_by(Medida.tipo.asc())
            .all()
        )

        gases = []
        for r in rows:
            tipo = r.tipo.value if hasattr(r.tipo, "value") else str(r.tipo)
            gases.append({
                "tipo": tipo,
                "valor": float(r.valor) if r.valor is not None else None,
            })

        return gases

    def _get_latest_location_by_placa(self, db: Session, placa_id: str):
        """
        Obtiene la última ubicación (lat, lon)
        registrada por una placa a partir de las medidas.
        """
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
        """
        Obtiene el registro de calidad del aire más cercano
        geográficamente a una ubicación dada.
        """
        dist2 = (
            (CalidadGeneral.lat - lat) * (CalidadGeneral.lat - lat) +
            (CalidadGeneral.lon - lon) * (CalidadGeneral.lon - lon)
        )

        return (
            db.query(CalidadGeneral)
            .order_by(dist2.asc(), desc(CalidadGeneral.fecha_hora))
            .first()
        )

    def obtener_home(
        self,
        db: Session,
        usuario_id: str,
        lat: float | None = None,
        lon: float | None = None
    ):
        """
        Construye la respuesta completa del Home del usuario.
        """
        user = (
            db.query(Usuario)
            .filter(Usuario.usuario_id == usuario_id)
            .first()
        )

        nombre_visible = (
            (user.nombre or "").strip()
            if user else "Usuario"
        )

        # ----------------------------
        # Último trayecto del usuario
        # ----------------------------
        ultimo = self._get_ultimo_trayecto(db, usuario_id)

        bicicleta_id = None
        ultimo_trayecto = None

        if ultimo:
            bicicleta_id = (
                str(ultimo.bicicleta_id)
                if ultimo.bicicleta_id else None
            )

            distancia_km = (
                float(ultimo.distancia_total)
                if ultimo.distancia_total is not None
                else None
            )

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

        # ----------------------------
        # Obtención de placa_id
        # ----------------------------
        placa_id = self._get_placa_id_by_bicicleta(db, bicicleta_id)

        # Fallback: última placa con medidas disponibles
        if not placa_id:
            m_any = (
                db.query(Medida)
                .order_by(desc(Medida.fecha_hora))
                .first()
            )
            placa_id = str(m_any.placa_id) if m_any else None

        # ----------------------------
        # Gases actuales
        # ----------------------------
        gases = (
            self._get_latest_gases_by_placa(db, placa_id)
            if placa_id else []
        )

        nivel_actual = {"gases": gases}

        # ----------------------------
        # Ubicación: GPS > última medida de la placa
        # ----------------------------
        if (lat is None or lon is None) and placa_id:
            loc = self._get_latest_location_by_placa(db, placa_id)
            if loc:
                lat, lon = loc

        # ----------------------------
        # Calidad del aire
        # ----------------------------
        if lat is not None and lon is not None:
            cg = self._get_calidad_by_location(db, lat, lon)
        else:
            cg = (
                db.query(CalidadGeneral)
                .order_by(desc(CalidadGeneral.fecha_hora))
                .first()
            )

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

        # ----------------------------
        # Impacto ambiental (simplificado)
        # ----------------------------
        rutas = (
            db.query(func.count(Trayecto.trayecto_id))
            .filter(Trayecto.usuario_id == usuario_id)
            .scalar()
            or 0
        )

        impacto = {
            "rutas_limpias": int(rutas),
            "co2_kg": 0.0,
            "puntos": 0
        }

        # ----------------------------
        # Respuesta final
        # ----------------------------
        return {
            "usuario": {
                "usuario_id": usuario_id,
                "nombre_visible": nombre_visible
            },
            "placa_id": placa_id,
            "calidad_aire": calidad_aire,
            "nivel_actual": nivel_actual,
            "impacto": impacto,
            "ultimo_trayecto": ultimo_trayecto,
        }
