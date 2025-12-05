# File: backend/db/seed.py (MODIFICADO)
import os
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from db.database import SessionLocal, Base, engine
from db.models import (
    Rol, Usuario, Mibisivalencia, Estacion, Bicicleta,
    PlacaSensores, Trayecto, Medida, Incidencia,
    TipoMedidaEnum, EstadoBicicleta, EstadoIncidencia, FuenteReporte,
    Recompensa, RecompensaUsuario, RecompensaObtenida,
    Interpolada, CalidadGeneral
)
from passlib.context import CryptContext
import uuid
from datetime import datetime, timezone, timedelta
import random

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generar_dni_valido(numero: int) -> str:
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    letra = letras[numero % 23]
    return f"{numero:08d}{letra}"

CARNES_DNI = [generar_dni_valido(12345678 + i) for i in range(2000)]

def seed_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        rol_usuario = Rol(nombre="usuario", descripcion="Usuario estándar")
        rol_admin = Rol(nombre="admin", descripcion="Administrador")
        db.add_all([rol_usuario, rol_admin])
        db.commit()

        carnets = [Mibisivalencia(targeta_id=dni) for dni in CARNES_DNI]
        db.add_all(carnets)
        db.commit()

        hash1 = pwd_context.hash("Password123!")
        hash2 = pwd_context.hash("Admin123!")

        usuarios = []
        for i in range(2000):
            usuario = Usuario(
                usuario_id=str(uuid.uuid4()),
                targeta_id=CARNES_DNI[i],
                nombre=f"User{i}",
                apellido=f"Apellido{i}",
                correo=f"user{i}@fake.com",
                contrasena_hash=hash1
            )
            usuario.roles.append(rol_usuario)
            usuarios.append(usuario)

        usuario_admin = Usuario(
            usuario_id=str(uuid.uuid4()),
            targeta_id=None,
            nombre="Admin",
            apellido="Sistema",
            correo="admin@fake.com",
            contrasena_hash=hash2
        )
        usuario_admin.roles.append(rol_admin)
        usuario_admin.roles.append(rol_usuario)

        db.add_all(usuarios + [usuario_admin])
        db.commit()

        # CAMBIO 1: Estaciones en Grau i Platja de Gandia
        estaciones_info = [
            ("Estación Renfe Gandia", 38.9665, -0.1830),
            ("Grau - Puerto", 38.9960, -0.1660),
            ("Platja - Club Náutico", 39.0010, -0.1630),
            ("Platja - Hotel Bayren", 39.0080, -0.1690),
            ("Platja - Final Paseo", 39.0190, -0.1750),
            ("Campus UPV Gandia", 38.9955, -0.1670),
            ("Plaza Prado", 38.9640, -0.1800),
            ("Hospital Francesc de Borja", 38.9580, -0.1900),
            ("Centro Histórico", 38.9670, -0.1810),
            ("Polideportivo", 38.9620, -0.1850)
        ]

        estaciones = [
            Estacion(estacion_id=i+1, nombre=info[0], lat=info[1], lon=info[2])
            for i, info in enumerate(estaciones_info)
        ]
        db.add_all(estaciones)
        db.commit()

        bicicletas = [
            Bicicleta(
                bicicleta_id=f"VLC{str(i+1).zfill(3)}",
                estacion_id=random.choice(estaciones).estacion_id,
                qr_code=f"QR-VLC{str(i+1).zfill(3)}",
                estado=EstadoBicicleta.estacionada
            ) for i in range(100)
        ]
        db.add_all(bicicletas)
        db.commit()

        placas = [
            PlacaSensores(
                placa_id=str(uuid.uuid4()),
                bicicleta_id=bicicletas[i].bicicleta_id,
                estado="activa",
                ult_actualizacion_estado=datetime.now(timezone.utc)
            ) for i in range(100)
        ]
        db.add_all(placas)
        db.commit()

        trayecto = Trayecto(
            trayecto_id=str(uuid.uuid4()),
            usuario_id=usuarios[0].usuario_id,
            bicicleta_id=bicicletas[0].bicicleta_id,
            fecha_inicio=datetime.now(timezone.utc) - timedelta(hours=1),
            origen_estacion_id=estaciones[0].estacion_id
        )
        db.add(trayecto)
        db.commit()

        db.add_all([
            Medida(
                lectura_id=str(uuid.uuid4()),
                placa_id=placas[0].placa_id,
                trayecto_id=trayecto.trayecto_id,
                fecha_hora=datetime.now(timezone.utc) - timedelta(minutes=10),
                tipo=TipoMedidaEnum.temperatura,
                valor=24.8,
                lat=39.0000, # Ajuste de latitud a Gandia
                lon=-0.1650  # Ajuste de longitud a Gandia
            )
        ])
        db.commit()

        incidencia = Incidencia(
            incidencia_id=str(uuid.uuid4()),
            usuario_id=usuarios[0].usuario_id,
            bicicleta_id=bicicletas[0].bicicleta_id,
            descripcion="Rueda pinchada",
            estado=EstadoIncidencia.nuevo,
            fuente=FuenteReporte.web
        )
        db.add(incidencia)
        db.commit()

        r1 = Recompensa(
            recompensa_id=str(uuid.uuid4()),
            titulo="Bronce",
            descripcion="Supera 10 km",
            fecha_inicio=datetime.now(timezone.utc),
            fecha_fin=datetime.now(timezone.utc) + timedelta(days=30),
            criterio_num_km=10.0
        )
        r2 = Recompensa(
            recompensa_id=str(uuid.uuid4()),
            titulo="Plata",
            descripcion="Supera 50 km",
            fecha_inicio=datetime.now(timezone.utc),
            fecha_fin=datetime.now(timezone.utc) + timedelta(days=30),
            criterio_num_km=50.0
        )
        db.add_all([r1, r2])
        db.commit()

        ru = RecompensaUsuario(
            usuario_id=usuarios[0].usuario_id,
            km_acumulados=37.5
        )
        db.add(ru)
        db.commit()

        ro = RecompensaObtenida(
            usuario_id=usuarios[0].usuario_id,
            recompensa_id=r1.recompensa_id,
            codigo_unico="CODIGO123ABC"
        )
        db.add(ro)
        db.commit()

        i1 = Interpolada(
            lectura_id=str(uuid.uuid4()),
            fecha_hora=datetime.now(timezone.utc),
            tipo=TipoMedidaEnum.pm10,
            lat=39.0000, # Ajuste de latitud a Gandia
            lon=-0.1650, # Ajuste de longitud a Gandia
            valor=28.4
        )
        i2 = Interpolada(
            lectura_id=str(uuid.uuid4()),
            fecha_hora=datetime.now(timezone.utc),
            tipo=TipoMedidaEnum.co,
            lat=39.0010, # Ajuste de latitud a Gandia
            lon=-0.1660, # Ajuste de longitud a Gandia
            valor=6.2
        )
        db.add_all([i1, i2])
        db.commit()

        cg = CalidadGeneral(
            valor_id=str(uuid.uuid4()),
            valor=72.5,
            color="verde",
            fecha_hora=datetime.now(timezone.utc),
            lat=39.0000, # Ajuste de latitud a Gandia
            lon=-0.1650  # Ajuste de longitud a Gandia
        )
        db.add(cg)
        db.commit()

        # Modified part: Generate lots of Medida for different gases and days
        gases = [TipoMedidaEnum.pm2_5, TipoMedidaEnum.pm10, TipoMedidaEnum.no2, TipoMedidaEnum.o3]
        num_days = 7
        
        # CAMBIO 2: Aumentar densidad de 50 a 800
        num_medidas_per_gas_per_day = 800 
        
        # CAMBIO 3: Coordenadas de generación en Grau i Platja de Gandia
        lat_min, lat_max = 38.9800, 39.0300
        lon_min, lon_max = -0.1900, -0.1400
        
        value_ranges = {
            TipoMedidaEnum.pm2_5: (0, 100),
            TipoMedidaEnum.pm10: (0, 200),
            TipoMedidaEnum.no2: (0, 200),
            TipoMedidaEnum.o3: (0, 0.2)  # in ppm
        }
        
        print(f"Generando {num_medidas_per_gas_per_day * len(gases) * num_days} medidas masivas...")

        for day in range(num_days):
            base_date = datetime.now(timezone.utc) - timedelta(days=day)
            for gas in gases:
                for _ in range(num_medidas_per_gas_per_day):
                    hour = random.randint(0, 23)
                    minute = random.randint(0, 59)
                    fh = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    lat = round(random.uniform(lat_min, lat_max), 4)
                    lon = round(random.uniform(lon_min, lon_max), 4)
                    valor = round(random.uniform(*value_ranges[gas]), 2)
                    medida = Medida(
                        lectura_id=str(uuid.uuid4()),
                        placa_id=random.choice(placas).placa_id,
                        trayecto_id=trayecto.trayecto_id,  # Reuse trayecto
                        fecha_hora=fh,
                        tipo=gas,
                        valor=valor,
                        lat=lat,
                        lon=lon
                    )
                    db.add(medida)
            db.commit() 

        # For interpolada and calidad, they can be generated by logic, so not populating here

        print("Seed completo con nuevas tablas")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
