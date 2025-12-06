# File: backend/db/seed.py
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
import random
import uuid

# Removed sys.path hack. 
# Run this script as: python -m backend.db.seed from the webapp/ directory.

from backend.db.database import SessionLocal, Base, engine
from backend.db.models import (
    Rol, Usuario, Mibisivalencia, Estacion, Bicicleta,
    PlacaSensores, Trayecto, Medida, Incidencia,
    TipoMedidaEnum, EstadoBicicleta, EstadoIncidencia, FuenteReporte,
    Recompensa, RecompensaUsuario, RecompensaObtenida,
    Interpolada, CalidadGeneral
)
# from backend.logic.mapas import LogicaMapas
from backend.pojos.posicion_gps import PosicionGPS
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generar_dni_valido(numero: int) -> str:
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    letra = letras[numero % 23]
    return f"{numero:08d}{letra}"

CARNES_DNI = [generar_dni_valido(12345678 + i) for i in range(2000)]

def seed_data():
    print("Iniciando seed...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Roles & Users
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
        for i in range(10): # Reduce users for speed
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
        usuarios.append(usuario_admin)

        db.add_all(usuarios)
        db.commit()

        # Estaciones
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
        
        estaciones = [Estacion(estacion_id=i+1, nombre=info[0], lat=info[1], lon=info[2]) for i, info in enumerate(estaciones_info)]
        db.add_all(estaciones)
        db.commit()

        # Bicicletas & Placas
        bicicletas = []
        placas = []
        for i in range(50):
            b = Bicicleta(
                bicicleta_id=f"VLC{str(i+1).zfill(3)}",
                estacion_id=random.choice(estaciones).estacion_id,
                qr_code=f"QR{i}",
                estado=EstadoBicicleta.estacionada
            )
            bicicletas.append(b)
            p = PlacaSensores(
                placa_id=str(uuid.uuid4()),
                bicicleta_id=b.bicicleta_id,
                estado="activa",
                ult_actualizacion_estado=datetime.now(timezone.utc)
            )
            placas.append(p)
        
        db.add_all(bicicletas)
        db.add_all(placas)
        db.commit()

        trayecto = Trayecto(
            trayecto_id=str(uuid.uuid4()),
            usuario_id=usuarios[0].usuario_id,
            bicicleta_id=bicicletas[0].bicicleta_id,
            fecha_inicio=datetime.now(timezone.utc),
            origen_estacion_id=estaciones[0].estacion_id
        )
        db.add(trayecto)
        db.commit()

        # ---------------------------------------------------------
        # GENERACIÓN MASIVA DE MEDIDAS (BANDAS DE COLOR)
        # ---------------------------------------------------------
        print("Generando medidas masivas en franjas...")
        gases = [TipoMedidaEnum.pm2_5, TipoMedidaEnum.pm10, TipoMedidaEnum.no2, TipoMedidaEnum.o3]
        
        # Franjas aproximadas en Gandia (Playa)
        # Latitudes: Min 38.9800, Max 39.0300
        # Lon: -0.1900 a -0.1400
        
        # Franja 1 (ROJO - Alta contaminación) - Norte
        b1_lat_min, b1_lat_max = 39.0150, 39.0300
        # Franja 2 (AMARILLO - Media contaminación) - Centro
        b2_lat_min, b2_lat_max = 39.0000, 39.0150
        # Franja 3 (VERDE - Baja contaminación) - Sur
        b3_lat_min, b3_lat_max = 38.9800, 39.0000
        
        lon_min, lon_max = -0.1800, -0.1500
        
        num_puntos_por_franja = 500 # Puntos masivos por franja y por hora
        
        # Vamos a generar datos para HOY (para que se vean en el mapa por defecto)
        hoy = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Generamos para algunas horas especificas (ej. 10, 11, 12, 13)
        horas_a_generar = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        
        medidas_batch = []
        
        def get_value_for_color(gas, color):
            # PM2.5: Good 0-9, Mod 9-35, Bad >35
            if gas == TipoMedidaEnum.pm2_5:
                return random.uniform(0, 9) if color == 'verde' else random.uniform(9.1, 35) if color == 'amarillo' else random.uniform(35.5, 100)
            # PM10: Good 0-54, Mod 55-154, Bad >155
            if gas == TipoMedidaEnum.pm10:
                return random.uniform(0, 54) if color == 'verde' else random.uniform(55, 154) if color == 'amarillo' else random.uniform(155, 300)
            # NO2: Good 0-53, Mod 54-100, Bad >101
            if gas == TipoMedidaEnum.no2:
                return random.uniform(0, 53) if color == 'verde' else random.uniform(54, 100) if color == 'amarillo' else random.uniform(101, 200)
            # O3: Good 0-0.054, Mod 0.055-0.070, Bad >0.071
            if gas == TipoMedidaEnum.o3:
                return random.uniform(0, 0.054) if color == 'verde' else random.uniform(0.055, 0.070) if color == 'amarillo' else random.uniform(0.071, 0.150)
            return 0
            
        for h in horas_a_generar:
            fecha_hora = hoy.replace(hour=h)
            
            # Franja ROJA
            for _ in range(num_puntos_por_franja):
                for gas in gases:
                    medidas_batch.append(Medida(
                        lectura_id=str(uuid.uuid4()),
                        placa_id=random.choice(placas).placa_id,
                        trayecto_id=trayecto.trayecto_id,
                        fecha_hora=fecha_hora + timedelta(minutes=random.randint(0, 59)),
                        tipo=gas,
                        valor=get_value_for_color(gas, 'rojo'),
                        lat=random.uniform(b1_lat_min, b1_lat_max),
                        lon=random.uniform(lon_min, lon_max)
                    ))

            # Franja AMARILLA
            for _ in range(num_puntos_por_franja):
                for gas in gases:
                    medidas_batch.append(Medida(
                        lectura_id=str(uuid.uuid4()),
                        placa_id=random.choice(placas).placa_id,
                        trayecto_id=trayecto.trayecto_id,
                        fecha_hora=fecha_hora + timedelta(minutes=random.randint(0, 59)),
                        tipo=gas,
                        valor=get_value_for_color(gas, 'amarillo'),
                        lat=random.uniform(b2_lat_min, b2_lat_max),
                        lon=random.uniform(lon_min, lon_max)
                    ))
                    
            # Franja VERDE
            for _ in range(num_puntos_por_franja):
                for gas in gases:
                    medidas_batch.append(Medida(
                        lectura_id=str(uuid.uuid4()),
                        placa_id=random.choice(placas).placa_id,
                        trayecto_id=trayecto.trayecto_id,
                        fecha_hora=fecha_hora + timedelta(minutes=random.randint(0, 59)),
                        tipo=gas,
                        valor=get_value_for_color(gas, 'verde'),
                        lat=random.uniform(b3_lat_min, b3_lat_max),
                        lon=random.uniform(lon_min, lon_max)
                    ))
            
            # Commit simple por hora para no explotar memoria
            db.add_all(medidas_batch)
            db.commit()
            medidas_batch = []
            print(f"Hora {h} generada...")

        # ---------------------------------------------------------
        # GENERACIÓN COMPLETADA
        # ---------------------------------------------------------
        print("Datos de sensores (medidas) generados correctamente.")

        
    except Exception as e:
        db.rollback()
        print(f"Error en seed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
