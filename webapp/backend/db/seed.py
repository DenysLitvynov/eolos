"""
Autor: Denys Litvynov Lymanets
Fecha: 03-12-2025
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

# 2000 carnets reales para pruebas
CARNES_DNI = [generar_dni_valido(12345678 + i) for i in range(2000)]

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
        rol_tecnico = Rol(nombre="tecnico", descripcion="Tecnico")

        db.add_all([rol_usuario, rol_admin,rol_tecnico])
        db.commit()

        # ---------------------------------------------------------

        # 2. Mibisivalencia - 2000 carnets reales
        carnets = [Mibisivalencia(targeta_id=dni) for dni in CARNES_DNI]
        db.add_all(carnets)
        db.commit()

        # ---------------------------------------------------------

        # 3. Usuarios de prueba
        hash1 = pwd_context.hash("Password123!")
        hash2 = pwd_context.hash("Admin123!")
        hash3= pwd_context.hash("Tech123!")

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
        usuario_tecnico = Usuario(
            usuario_id=str(uuid.uuid4()),
            targeta_id=None,
            nombre="Marc",
            apellido="Roig",
            correo="tecnico@fake.com",
            contrasena_hash=hash3
        )
        usuario_admin.roles.append(rol_admin)
        usuario_admin.roles.append(rol_usuario)
        usuario_tecnico.roles.append(rol_tecnico)

        db.add_all(usuarios + [usuario_admin])
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

        # 5. Bicicletas (2000) VLC0001 - VLC2000
        bicicletas = []
        for i in range(1, 2001):
            code = f"VLC{i:04d}"
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
            usuario_id=usuarios[0].usuario_id,
            bicicleta_id=ejemplo_bici.bicicleta_id,
            fecha_inicio=datetime.now(timezone.utc) - timedelta(minutes=30),
            fecha_fin=None,
            origen_estacion_id=ejemplo_bici.estacion_id,
            distancia_total=4.2
        )
        db.add(trayecto)
        db.commit()

        # ---------------------------------------------------------
        # ---------------------------------------------------------
        # 8. Medidas FAKE – verde/amarillo/rojo – Gandia

        def generar_medidas_fake(db, placas):
            import uuid
            from datetime import datetime, timezone, timedelta
            import random
            from db.models import Medida, TipoMedidaEnum

            now = datetime.now(timezone.utc)

            # ------------ COORDENADAS REALES DE PLATJA I GRAU DE GANDIA --------------
            LAT_MIN = 38.9865
            LAT_MAX = 39.0035
            LON_MIN = -0.1735
            LON_MAX = -0.1485
            # --------------------------------------------------------------------------

            RANGOS = {
                "verde": {
                    TipoMedidaEnum.o3: (0, 80),
                    TipoMedidaEnum.no2: (0, 30),
                    TipoMedidaEnum.co: (0, 5),
                    TipoMedidaEnum.pm2_5:(1, 12),
                    TipoMedidaEnum.pm10:(5, 25),
                },
                "amarillo": {
                    TipoMedidaEnum.o3: (100, 120),
                    TipoMedidaEnum.no2: (40, 120),
                    TipoMedidaEnum.co: (5, 10),
                    TipoMedidaEnum.pm2_5:(12, 25),
                    TipoMedidaEnum.pm10:(25, 50),
                },
                "rojo": {
                    TipoMedidaEnum.o3: (120, 180),
                    TipoMedidaEnum.no2: (200, 280),
                    TipoMedidaEnum.co: (10, 18),
                    TipoMedidaEnum.pm2_5:(25, 60),
                    TipoMedidaEnum.pm10:(50, 120),
                }
            }

            medidas = []
            POR_FRANJA = 5000
            orden = ["verde", "amarillo", "rojo"]

            for franja in orden:
                for _ in range(POR_FRANJA):
                    placa = random.choice(placas)

                    lat = random.uniform(LAT_MIN, LAT_MAX)
                    lon = random.uniform(LON_MIN, LON_MAX)
                    fecha = now - timedelta(hours=random.uniform(0, 48))

                    tipo = random.choice(list(RANGOS[franja].keys()))
                    vmin, vmax = RANGOS[franja][tipo]
                    valor = random.uniform(vmin, vmax)

                    medidas.append(
                        Medida(
                            lectura_id=str(uuid.uuid4()),
                            placa_id=placa.placa_id,
                            trayecto_id=None,
                            fecha_hora=fecha,
                            tipo=tipo,
                            valor=valor,
                            lat=lat,
                            lon=lon
                        )
                    )

            db.add_all(medidas)
            db.commit()

        # Ejecutar tras placas
        placas_all = db.query(PlacaSensores).all()
        generar_medidas_fake(db, placas_all)

        print("Medidas FAKE (Gandia) generadas correctamente.")

        # 9. Incidencia de ejemplo
        incidencia_tec1 = Incidencia(
            incidencia_id=str(uuid.uuid4()),
            usuario_id=usuarios[0].usuario_id,
            bicicleta_id=bicicletas[0].bicicleta_id,
            descripcion="Rueda pinchada",
            estado=EstadoIncidencia.nuevo,
            fuente=FuenteReporte.bici
        )
        db.add(incidencia_tec1)
        db.commit()
        
        incidencia_tec2 = Incidencia(
            incidencia_id=str(uuid.uuid4()),
            usuario_id=usuario_normal.usuario_id,
            bicicleta_id=bicicletas[0].bicicleta_id,
            descripcion="Bici Vandalizada",
            estado=EstadoIncidencia.nuevo,
            fuente=FuenteReporte.bici
        )
        db.add(incidencia_tec2)
        db.commit()
        
        incidencia_admin = Incidencia(
            incidencia_id=str(uuid.uuid4()),
            usuario_id=usuario_normal.usuario_id,
            bicicleta_id=bicicletas[0].bicicleta_id,#estas incidencias en bicicleta ID deberian tener un 0 o algo pa distinguirlas de las del tecnico
            descripcion="Error al canjear recompensas",
            estado=EstadoIncidencia.nuevo,
            fuente=FuenteReporte.web
        )
        db.add(incidencia_admin)
        db.commit()
        
        
        incidencia_admin2 = Incidencia(
            incidencia_id=str(uuid.uuid4()),
            usuario_id=usuario_normal.usuario_id,
            bicicleta_id=bicicletas[0].bicicleta_id,#estas incidencias en bicicleta ID deberian tener un 0 o algo pa distinguirlas de las del tecnico
            descripcion="Error al escanear QR",
            estado=EstadoIncidencia.nuevo,
            fuente=FuenteReporte.app
        )
        db.add(incidencia_admin2)
        db.commit()

        print("Seed completado: 2000 carnets DNI válidos + 2000 usuarios + estaciones + 2000 bicis + placas + trayecto + medidas + incidencia")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

# ---------------------------------------------------------

if __name__ == "__main__":
    seed_data()
