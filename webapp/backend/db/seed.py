"""
Autor: Denys Litvynov Lymanets
Fecha: 15-11-2025
Descripción: Script para poblar todas las tablas de la base de datos con unos pocos datos de prueba.  
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
from datetime import datetime, timezone, timedelta
import random

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
    """
    Método para poblar las tablas con datos simulados.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Roles
        rol_usuario = Rol(nombre="usuario", descripcion="Usuario estándar")
        rol_admin = Rol(nombre="admin", descripcion="Administrador")
        db.add_all([rol_usuario, rol_admin])
        db.commit()

        # ---------------------------------------------------------

        # 2. Mibisivalencia - 10 carnets reales
        carnets = [Mibisivalencia(targeta_id=dni) for dni in CARNES_DNI]
        db.add_all(carnets)
        db.commit()

        # ---------------------------------------------------------

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

        # ---------------------------------------------------------

        # 4. Estaciones (10 estaciones de Valencia) - sin capacidad
        estaciones_info = [
            ("Plaza del Ayuntamiento", 39.4699, -0.3763),
            ("Malvarrosa", 39.4780, -0.3266),
            ("Ruzafa", 39.4618, -0.3764),
            ("Benimaclet", 39.4901, -0.3619),
            ("Campanar", 39.4890, -0.4001),
            ("Patraix", 39.4572, -0.3972),
            ("Ciudad de las Artes", 39.4541, -0.3505),
            ("Turia - Puente de Serranos", 39.4787, -0.3769),
            ("Mestalla", 39.4746, -0.3585),
            ("Orriols", 39.5030, -0.3642),
        ]
        estaciones = []
        for nombre, lat, lon in estaciones_info:
            estaciones.append(Estacion(nombre=nombre, lat=lat, lon=lon))
        db.add_all(estaciones)
        db.commit()

        # ---------------------------------------------------------

        # 5. Bicicletas (50) VLC001 - VLC050
        bicicletas = []
        for i in range(1, 51):
            code = f"VLC{i:03d}"
            estacion = random.choice(estaciones)
            bici = Bicicleta(
                bicicleta_id=code,
                estacion_id=estacion.estacion_id,
                qr_code=f"QR-{code}",
                estado=random.choice(list(EstadoBicicleta))
            )
            bicicletas.append(bici)
        db.add_all(bicicletas)
        db.commit()

        # ---------------------------------------------------------

        # 6. Placas (una por bicicleta) con ult_actualizacion_estado
        placas = []
        for bici in bicicletas:
            placa = PlacaSensores(
                placa_id=str(uuid.uuid4()),
                bicicleta_id=bici.bicicleta_id,
                estado="activa",
                ult_actualizacion_estado=datetime.now(timezone.utc)
            )
            placas.append(placa)
        db.add_all(placas)
        db.commit()

        # ---------------------------------------------------------

        # 7. Trayecto de ejemplo (usar una de las bicicletas creadas)
        ejemplo_bici = random.choice(bicicletas)
        trayecto = Trayecto(
            trayecto_id=str(uuid.uuid4()),
            usuario_id=usuario_normal.usuario_id,
            bicicleta_id=ejemplo_bici.bicicleta_id,
            fecha_inicio=datetime.now(timezone.utc) - timedelta(minutes=30),
            fecha_fin=None,
            origen_estacion_id=ejemplo_bici.estacion_id,
            distancia_total=4.2
        )
        db.add(trayecto)
        db.commit()

        # ---------------------------------------------------------

        # 8. Medidas (2 ejemplos) asociadas a la placa de la bici del trayecto
        placa_rel = db.query(PlacaSensores).filter_by(bicicleta_id=ejemplo_bici.bicicleta_id).first()
        if placa_rel:
            medida1 = Medida(
                lectura_id=str(uuid.uuid4()),
                placa_id=placa_rel.placa_id,
                trayecto_id=trayecto.trayecto_id,
                fecha_hora=datetime.now(timezone.utc) - timedelta(minutes=20),
                tipo=TipoMedidaEnum.pm2_5,
                valor=12.5,
                lat=39.4750,
                lon=-0.3500
            )
            medida2 = Medida(
                lectura_id=str(uuid.uuid4()),
                placa_id=placa_rel.placa_id,
                trayecto_id=trayecto.trayecto_id,
                fecha_hora=datetime.now(timezone.utc) - timedelta(minutes=10),
                tipo=TipoMedidaEnum.temperatura,
                valor=24.8,
                lat=39.4760,
                lon=-0.3550
            )
            db.add_all([medida1, medida2])
            db.commit()

        # ---------------------------------------------------------

        # 9. Incidencia de ejemplo
        incidencia = Incidencia(
            incidencia_id=str(uuid.uuid4()),
            usuario_id=usuario_normal.usuario_id,
            bicicleta_id=bicicletas[0].bicicleta_id,
            descripcion="Rueda pinchada",
            estado=EstadoIncidencia.nuevo,
            fuente=FuenteReporte.web
        )
        db.add(incidencia)
        db.commit()

        print("Seed completado: 10 carnets DNI válidos + estaciones + 50 bicis + placas + trayecto + medidas + incidencia")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

# ---------------------------------------------------------

if __name__ == "__main__":
    seed_data()

