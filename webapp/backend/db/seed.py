"""
Autor: Denys Litvynov Lymanets
Fecha: 15-11-2025
Descripción: Seed con 10 carnets reales (DNI) + todo lo demás
"""

# ---------------------------------------------------------
import os
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from db.database import SessionLocal, Base, engine
from db.models import (
    Rol, Usuario, Mibisivalencia, Estacion, Bicicleta, 
    PlacaSensores, Trayecto, Medida, Incidencia,
    TipoMedidaEnum, EstadoBicicleta, EstadoIncidencia, FuenteReporte
)
from passlib.context import CryptContext
import uuid
from datetime import datetime, timezone

# ---------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generador de DNI válidos (8 números + letra correcta)
def generar_dni_valido(numero: int) -> str:
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    letra = letras[numero % 23]
    return f"{numero:08d}{letra}"

# 10 carnets reales para pruebas
CARNES_DNI = [
    generar_dni_valido(12345678),  # 12345678Z
    generar_dni_valido(87654321),  # 87654321T
    generar_dni_valido(11111111),  # 11111111H
    generar_dni_valido(22222222),  # 22222222Y
    generar_dni_valido(33333333),  # 33333333F
    generar_dni_valido(44444444),  # 44444444P
    generar_dni_valido(55555555),  # 55555555D
    generar_dni_valido(66666666),  # 66666666X
    generar_dni_valido(77777777),  # 77777777B
    generar_dni_valido(88888888),  # 88888888N
]

def seed_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Roles
        rol_usuario = Rol(nombre="usuario", descripcion="Usuario estándar")
        rol_admin = Rol(nombre="admin", descripcion="Administrador")
        db.add_all([rol_usuario, rol_admin])
        db.commit()

        # 2. Mibisivalencia - 10 carnets reales
        carnets = [Mibisivalencia(targeta_id=dni) for dni in CARNES_DNI]
        db.add_all(carnets)
        db.commit()

        # 3. Usuarios de prueba
        hash1 = pwd_context.hash("Password123!")
        hash2 = pwd_context.hash("Admin123!")

        usuario_normal = Usuario(
            usuario_id=str(uuid.uuid4()),
            targeta_id=CARNES_DNI[0],  # 12345678Z
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

        usuario_normal.roles.append(rol_usuario)
        usuario_admin.roles.append(rol_admin)
        usuario_admin.roles.append(rol_usuario)

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

        # 6. Placas
        placa1 = PlacaSensores(placa_id=str(uuid.uuid4()), bicicleta_id=bici1.bicicleta_id, estado="activa")
        placa2 = PlacaSensores(placa_id=str(uuid.uuid4()), bicicleta_id=bici2.bicicleta_id, estado="activa")
        db.add_all([placa1, placa2])
        db.commit()

        # 7. Trayecto
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
        print("Seed completado: 10 carnets DNI válidos + todo lo demás")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
