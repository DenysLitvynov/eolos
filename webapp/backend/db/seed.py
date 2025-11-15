"""
Autor: Denys Litvynov Lymanets
Fecha: 15-11-2025
Descripción: Script para insertar datos de prueba (seeds) en la BD. 
Ejecutar: python backend/db/seed.py   (o desde cualquier sitio)
"""

# ---------------------------------------------------------
# SOLUCIÓN AL ImportError → añadimos backend al path para que funcione siempre
import os
import sys
from pathlib import Path

# Añadimos la carpeta backend al path (así los imports absolutos funcionan aunque ejecutes el script directamente)
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

# Ahora los imports son absolutos dentro del paquete backend
from db.database import SessionLocal, Base, engine
from db.models import (
    Rol, Usuario, Mibisivalencia, Estacion, Bicicleta, 
    PlacaSensores, Trayecto, Medida, Incidencia,
    TipoMedidaEnum, EstadoBicicleta, EstadoIncidencia, FuenteReporte
)
# ---------------------------------------------------------

from passlib.context import CryptContext
import uuid
from datetime import datetime, timezone

# ---------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_data():
    # Recrear todas las tablas con la nueva estructura
    Base.metadata.drop_all(bind=engine)      # ← BORRA TODO lo anterior
    Base.metadata.create_all(bind=engine)    # ← Crea las 12 tablas nuevas

    db = SessionLocal()
    try:
        # 1. Roles
        rol_usuario = Rol(nombre="usuario", descripcion="Usuario estándar")
        rol_admin = Rol(nombre="admin", descripcion="Administrador")
        db.add_all([rol_usuario, rol_admin])
        db.commit()

        # 2. Mibisivalencia (targetas válidas) - ahora UUID
        targeta1_id = str(uuid.uuid4())
        targeta2_id = str(uuid.uuid4())
        carnet1 = Mibisivalencia(targeta_id=targeta1_id)
        carnet2 = Mibisivalencia(targeta_id=targeta2_id)
        db.add_all([carnet1, carnet2])
        db.commit()

        # 3. Usuarios de prueba
        hash1 = pwd_context.hash("Password123!")
        hash2 = pwd_context.hash("Admin123!")

        usuario_normal = Usuario(
            usuario_id=str(uuid.uuid4()),
            targeta_id=targeta1_id,
            nombre="Pepe",
            apellido="García",
            correo="pepe@fake.com",
            contrasena_hash=hash1
        )
        usuario_admin = Usuario(
            usuario_id=str(uuid.uuid4()),
            targeta_id=None,
            nombre="Admin",
            apellido="Sistema",
            correo="admin@fake.com",
            contrasena_hash=hash2
        )

        # Asignar roles
        usuario_normal.roles.append(rol_usuario)
        usuario_admin.roles.append(rol_admin)
        usuario_admin.roles.append(rol_usuario)  # el admin también tiene rol usuario

        db.add_all([usuario_normal, usuario_admin])
        db.commit()

        # 4. Estaciones
        est1 = Estacion(nombre="Estación 001 - Plaza del Ayuntamiento", lat=39.4699, lon=-0.3763, capacidad=30)
        est2 = Estacion(nombre="Estación 045 - Malvarrosa", lat=39.4780, lon=-0.3266, capacidad=25)
        db.add_all([est1, est2])
        db.commit()

        # 5. Bicicletas
        bici1 = Bicicleta(
            bicicleta_id=str(uuid.uuid4()),
            estacion_id=est1.estacion_id,
            qr_code="QR-VAL-001-ABC123",
            short_code="VLC001",
            estado=EstadoBicicleta.estacionada
        )
        bici2 = Bicicleta(
            bicicleta_id=str(uuid.uuid4()),
            estacion_id=est2.estacion_id,
            qr_code="QR-VAL-045-XYZ789",
            short_code="VLC045",
            estado=EstadoBicicleta.en_uso
        )
        db.add_all([bici1, bici2])
        db.commit()

        # 6. Placas sensores
        placa1 = PlacaSensores(placa_id=str(uuid.uuid4()), bicicleta_id=bici1.bicicleta_id, estado="activa")
        placa2 = PlacaSensores(placa_id=str(uuid.uuid4()), bicicleta_id=bici2.bicicleta_id, estado="activa")
        db.add_all([placa1, placa2])
        db.commit()

        # 7. Trayecto de ejemplo
        trayecto = Trayecto(
            trayecto_id=str(uuid.uuid4()),
            usuario_id=usuario_normal.usuario_id,
            bicicleta_id=bici2.bicicleta_id,
            fecha_inicio=datetime.now(timezone.utc),
            origen_estacion_id=est2.estacion_id,
            distancia_total=4.2
        )
        db.add(trayecto)
        db.commit()

        # 8. Medidas
        medida1 = Medida(
            lectura_id=str(uuid.uuid4()),
            placa_id=placa2.placa_id,
            trayecto_id=trayecto.trayecto_id,
            fecha_hora=datetime.now(timezone.utc),
            tipo=TipoMedidaEnum.pm2_5,
            valor=12.5,
            lat=39.4750,
            lon=-0.3500
        )
        medida2 = Medida(
            lectura_id=str(uuid.uuid4()),
            placa_id=placa2.placa_id,
            trayecto_id=trayecto.trayecto_id,
            fecha_hora=datetime.now(timezone.utc),
            tipo=TipoMedidaEnum.temperatura,
            valor=24.8,
            lat=39.4760,
            lon=-0.3550
        )
        db.add_all([medida1, medida2])

        # 9. Incidencia
        incidencia = Incidencia(
            incidencia_id=str(uuid.uuid4()),
            usuario_id=usuario_normal.usuario_id,
            bicicleta_id=bici1.bicicleta_id,
            descripcion="Rueda pinchada",
            estado=EstadoIncidencia.nuevo,
            fuente=FuenteReporte.web
        )
        db.add(incidencia)

        db.commit()
        print("✅ Seed completado perfectamente – 15-11-2025")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
