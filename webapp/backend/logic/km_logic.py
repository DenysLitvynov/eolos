"""
Autor: JINWEI
Fecha: 28-12-2025
Descripción: Lógica para km acumulados y descuento (extraído desde recompensas.descripcion).
"""

from sqlalchemy.orm import Session
from sqlalchemy import text


class LogicaKm:
    def obtener_resumen(self, db: Session, usuario_id: str):
        # 1) km acumulados
        sql_km = text("""
            SELECT COALESCE(ru.km_acumulados, 0) AS km
            FROM public.recompensas_usuario ru
            WHERE ru.usuario_id = :usuario_id
        """)

        km_row = db.execute(sql_km, {"usuario_id": usuario_id}).mappings().first()
        km = float(km_row["km"]) if km_row and km_row["km"] is not None else 0.0

        # 2) descuento acumulado（从 descripcion 提取数字）
        sql_desc = text("""
            SELECT COALESCE(SUM(
                NULLIF(regexp_replace(r.descripcion, '[^0-9.]', '', 'g'), '')::double precision
            ), 0) AS descuento
            FROM public.recompensas_obtenidas ro
            JOIN public.recompensas r
              ON r.recompensa_id = ro.recompensa_id
            WHERE ro.usuario_id = :usuario_id
        """)

        d_row = db.execute(sql_desc, {"usuario_id": usuario_id}).mappings().first()
        descuento = float(d_row["descuento"]) if d_row and d_row["descuento"] is not None else 0.0

        return km, descuento
