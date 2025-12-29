"""
Autor: JINWEI
Fecha: 28-12-2025
Descripción: Lógica para obtener contaminación por estación (punto más cercano en calidad_general).
"""

from sqlalchemy.orm import Session
from sqlalchemy import text


class LogicaContaminacion:
    def obtener_contaminacion_por_estaciones(self, db: Session, limit: int = 10):
        """
        - Obtiene las primeras estaciones (por estacion_id).
        - Para cada estación busca el punto más cercano en calidad_general.
        - Distancia aproximada sin PostGIS: (dlat^2 + dlon^2).
        """

        sql = text("""
            SELECT
              e.estacion_id,
              e.nombre AS estacion_nombre,
              e.lat    AS estacion_lat,
              e.lon    AS estacion_lon,

              cg.valor AS valor,
              cg.color AS color,
              cg.fecha_hora AS fecha_hora,
              cg.lat   AS punto_lat,
              cg.lon   AS punto_lon
            FROM estaciones e
            JOIN LATERAL (
              SELECT cg2.*
              FROM calidad_general cg2
              ORDER BY ((cg2.lat - e.lat)^2 + (cg2.lon - e.lon)^2) ASC
              LIMIT 1
            ) cg ON true
            ORDER BY e.estacion_id
            LIMIT :limit;
        """)

        rows = db.execute(sql, {"limit": limit}).mappings().all()

        items = []
        for r in rows:
            items.append({
                "estacion_id": int(r["estacion_id"]),
                "nombre": r["estacion_nombre"],
                "estacion": {
                    "lat": float(r["estacion_lat"]),
                    "lon": float(r["estacion_lon"]),
                },
                "medicion": {
                    "valor": float(r["valor"]) if r["valor"] is not None else None,
                    "color": r["color"],
                    "fecha_hora": r["fecha_hora"].isoformat() if r["fecha_hora"] else None,
                    "punto": {
                        "lat": float(r["punto_lat"]) if r["punto_lat"] is not None else None,
                        "lon": float(r["punto_lon"]) if r["punto_lon"] is not None else None,
                    }
                }
            })

        return items
