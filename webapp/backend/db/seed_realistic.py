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
    TipoMedidaEnum, EstadoBicicleta, EstadoIncidencia, FuenteReporte,Recompensa
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
        rol_tecnico = Rol(nombre="tecnico", descripcion="Técnico de mantenimiento")
        rol_tecnico_ayuntamiento = Rol(nombre="tecnico_ayuntamiento", descripcion="Administrador del Ayuntamiento")
        rol_tecnico_mapas = Rol(nombre="tecnico_mapas", descripcion="tecnico_mapas")


          
        db.add_all([rol_usuario, rol_admin])
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
        hash3 = pwd_context.hash("Tecnico123!")
        hash4 = pwd_context.hash("Ayu123!")


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
            nombre="Tecnico",
            apellido="Sensores",
            correo="tecnico@fake.com",
            contrasena_hash=hash3
        )
        
        usuario_ayuntamiento = Usuario(
            usuario_id=str(uuid.uuid4()),
            targeta_id=None,
            nombre="TecAyu",
            apellido="Ayunamiento",
            correo="ayuntamiento@fake.com",
            contrasena_hash=hash4
        )
        
        usuario_admin_mapas = Usuario(
            usuario_id=str(uuid.uuid4()),
            targeta_id=None,
            nombre="TecMap",
            apellido="Mapas",
            correo="mapas@fake.com",
            contrasena_hash=hash1
        )
        
        
        
        usuario_admin.roles.append(rol_admin)
        usuario_admin.roles.append(rol_usuario)
        usuario_tecnico.roles.append(rol_tecnico)
        usuario_ayuntamiento.roles.append(rol_tecnico_ayuntamiento)
        usuario_admin_mapas.roles.append(rol_tecnico_mapas)

        db.add_all(usuarios + [usuario_admin]+ [usuario_tecnico]+ [usuario_ayuntamiento]+ [usuario_admin_mapas])
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
        # 8. Medidas REALISTAS – adaptadas a Platja i Grau de Gandia

        def generar_medidas_realistas(db, placas):
            import uuid
            from datetime import datetime, timezone, timedelta
            import random
            from db.models import Medida, TipoMedidaEnum

            now = datetime.now(timezone.utc)

            # Rango oficial del PDF + PMs normales
            RANGOS = {
                TipoMedidaEnum.o3:   (0, 140),
                TipoMedidaEnum.no2:  (0, 200),
                TipoMedidaEnum.co:   (0, 12),
                TipoMedidaEnum.pm2_5:(1, 50),
                TipoMedidaEnum.pm10: (5, 90),
            }

            # ------------ COORDENADAS REALES DE PLATJA I GRAU DE GANDIA --------------
            LAT_MIN = 38.9865
            LAT_MAX = 39.0035
            LON_MIN = -0.1735
            LON_MAX = -0.1485
            # --------------------------------------------------------------------------

            medidas = []
            TOTAL = 50000

            for _ in range(TOTAL):
                placa = random.choice(placas)

                lat = random.uniform(LAT_MIN, LAT_MAX)
                lon = random.uniform(LON_MIN, LON_MAX)

                fecha = now - timedelta(hours=random.uniform(0, 48))

                tipo = random.choice(list(RANGOS.keys()))
                vmin, vmax = RANGOS[tipo]
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

        # Ejecutar tras crear las placas
        placas_all = db.query(PlacaSensores).all()
        generar_medidas_realistas(db, placas_all)

        print("Medidas REALISTAS (Gandia) generadas correctamente.")


        # ---------------------------------------------------------

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
            usuario_id=usuario_admin.usuario_id,
            bicicleta_id=bicicletas[0].bicicleta_id,
            descripcion="Bici Vandalizada",
            estado=EstadoIncidencia.nuevo,
            fuente=FuenteReporte.bici
        )
        db.add(incidencia_tec2)
        db.commit()
        
        incidencia_admin = Incidencia(
            incidencia_id=str(uuid.uuid4()),
            usuario_id=usuario_admin.usuario_id,
            bicicleta_id=bicicletas[0].bicicleta_id,#estas incidencias en bicicleta ID deberian tener un 0 o algo pa distinguirlas de las del tecnico
            descripcion="Error al canjear recompensas",
            estado=EstadoIncidencia.nuevo,
            fuente=FuenteReporte.web
        )
        db.add(incidencia_admin)
        db.commit()
        
        
        incidencia_admin2 = Incidencia(
            incidencia_id=str(uuid.uuid4()),
            usuario_id=usuario_admin.usuario_id,
            bicicleta_id=bicicletas[0].bicicleta_id,#estas incidencias en bicicleta ID deberian tener un 0 o algo pa distinguirlas de las del tecnico
            descripcion="Error al escanear QR",
            estado=EstadoIncidencia.nuevo,
            fuente=FuenteReporte.app
        )
        db.add(incidencia_admin2)
        db.commit()
        
        
        # 10. Recompensas (10 instancias)
        now = datetime.now(timezone.utc)
        
        recompensas = [
            Recompensa(
                recompensa_id=str(uuid.uuid4()),  
                titulo="Descuento 10% Mcmenú",
                descripcion="Obtén un 10% de descuento en tu Mcmenú favorito. Válido por 3 meses.",
                fecha_inicio=now,
                fecha_fin=now + timedelta(days=90),
                criterio_num_km=10.0
            ),
            Recompensa(
                recompensa_id=str(uuid.uuid4()),  
                titulo="Corte + Lavado 30% OFF",
                descripcion="30% de descuento en peluquería El Estilista al completar 20km.",
                fecha_inicio=now,
                fecha_fin=now + timedelta(days=60),
                criterio_num_km=20.0
            ),
            Recompensa(
                recompensa_id=str(uuid.uuid4()),  
                titulo="Entrada Cine 2x1",
                descripcion="Dos entradas por el precio de una en Cines Babel. Requiere 50km.",
                fecha_inicio=now + timedelta(days=15), # Empieza más tarde
                fecha_fin=now + timedelta(days=120),
                criterio_num_km=50.0
            ),
            Recompensa(
                recompensa_id=str(uuid.uuid4()),  
                titulo="Café Gratis en Panaria",
                descripcion="Canjea un café mediano gratis en cualquier Panaria.",
                fecha_inicio=now - timedelta(days=5), # Recompensa ya activa
                fecha_fin=now + timedelta(days=30),
                criterio_num_km=5.0
            ),
            Recompensa(
                recompensa_id=str(uuid.uuid4()),  
                titulo="Bono Mantenimiento Bici",
                descripcion="Mantenimiento básico gratuito en Taller La Rueda.",
                fecha_inicio=now,
                fecha_fin=now + timedelta(days=180),
                criterio_num_km=100.0
            ),
            Recompensa(
                recompensa_id=str(uuid.uuid4()),
                titulo="Bolsa de Reutilizable Eolos",
                descripcion="Consigue nuestra bolsa ecológica oficial. 15km.",
                fecha_inicio=now,
                fecha_fin=now + timedelta(days=90),
                criterio_num_km=15.0
            ),
            Recompensa(
                recompensa_id=str(uuid.uuid4()),
                titulo="Helado Gratis",
                descripcion="Un helado pequeño de regalo en Heladería Frío Total.",
                fecha_inicio=now,
                fecha_fin=now + timedelta(days=30),
                criterio_num_km=10.0 # Repetido para que sea una recompensa 'disponible' fácil
            ),
            Recompensa(
                recompensa_id=str(uuid.uuid4()),
                titulo="Vale 5€ Decathlon",
                descripcion="Vale de 5€ para cualquier producto Decathlon.",
                fecha_inicio=now + timedelta(days=7),
                fecha_fin=now + timedelta(days=97),
                criterio_num_km=75.0
            ),
            Recompensa(
                recompensa_id=str(uuid.uuid4()),
                titulo="Llavero Eolos",
                descripcion="Llavero con el logo de la iniciativa.",
                fecha_inicio=now,
                fecha_fin=now + timedelta(days=365),
                criterio_num_km=2.0
            ),
            Recompensa(
                recompensa_id=str(uuid.uuid4()),
                titulo="Curso Online Gratuito",
                descripcion="Acceso gratuito a un curso de programación web (nivel básico). Requiere 200km.",
                fecha_inicio=now,
                fecha_fin=now + timedelta(days=365),
                criterio_num_km=200.0
            )
        ]
        # ---------------------------------------------------------
        db.add_all(recompensas)
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

