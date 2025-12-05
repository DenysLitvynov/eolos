"""
Autor: Denys Litvynov Lymanets
Fecha: 03-12-2025
Descripción: Script para generar JSONs con datos de la base de datos después de seed.
"""

import json
from db.database import SessionLocal
from db.models import Mibisivalencia, Estacion, Bicicleta

db = SessionLocal()
try:
    # Targetas
    targetas = [t.targeta_id for t in db.query(Mibisivalencia).all()]
    with open('targetas.json', 'w') as f:
        json.dump(targetas, f)

    # Estaciones
    estaciones = [
        {"estacion_id": e.estacion_id, "nombre": e.nombre, "lat": e.lat, "lon": e.lon}
        for e in db.query(Estacion).all()
    ]
    with open('estaciones.json', 'w') as f:
        json.dump(estaciones, f)

    # Bicicletas
    bicicletas = [
        {"bicicleta_id": b.bicicleta_id, "estacion_id": b.estacion_id, "qr_code": b.qr_code, "estado": b.estado}
        for b in db.query(Bicicleta).all()
    ]
    with open('bicicletas.json', 'w') as f:
        json.dump(bicicletas, f)

    print("JSONs generados: targetas.json, estaciones.json, bicicletas.json")
finally:
    db.close()
