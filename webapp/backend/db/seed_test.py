"""
Autor: Denys Litvynov Lymanets
Versión: Testing Optimizado
Descripción: Script para poblar la BD con datos reducidos pero completos para pruebas de interfaz.
"""

import os
import sys
from pathlib import Path
import uuid
from datetime import datetime, timezone, timedelta
import random
from passlib.context import CryptContext

# Configuración de rutas
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from db.database import SessionLocal, Base, engine
from db.models import (
    Rol, Usuario, Mibisivalencia, Estacion, Bicicleta, 
    PlacaSensores, Trayecto, Medida, Incidencia,
    TipoMedidaEnum, EstadoBicicleta, EstadoIncidencia, FuenteReporte, 
    Recompensa, RecompensaUsuario
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generar_dni_valido(numero: int) -> str:
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    letra = letras[numero % 23]
    return f"{numero:08d}{letra}"

# Reducimos a 10 para facilitar el testing
NUM_USUARIOS = 10
CARNES_DNI = [generar_dni_valido(12345678 + i) for i in range(NUM_USUARIOS)]

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

        # 2. Mibisivalencia
        carnets = [Mibisivalencia(targeta_id=dni) for dni in CARNES_DNI]
        db.add_all(carnets)
        db.commit()

        # 3. Usuarios (10 usuarios + 1 Admin)
        hash_comun = pwd_context.hash("Password123!")
        usuarios = []
        for i in range(NUM_USUARIOS):
            user = Usuario(
                usuario_id=str(uuid.uuid4()),
                targeta_id=CARNES_DNI[i],
                nombre=f"User{i}",
                apellido=f"Test",
                correo=f"user{i}@fake.com",
                contrasena_hash=hash_comun
            )
            user.roles.append(rol_usuario)
            usuarios.append(user)
        
        db.add_all(usuarios)
        db.commit()

        # 4. Estaciones
        estaciones_info = [
            ("Plaza del Ayuntamiento", 39.4699, -0.3763),
            ("Malvarrosa", 39.4780, -0.3266),
            ("Ruzafa", 39.4618, -0.3764)
        ]
        estaciones = [Estacion(nombre=n, lat=la, lon=lo) for n, la, lo in estaciones_info]
        db.add_all(estaciones)
        db.commit()

        # 5. Bicicletas (20 bicis)
        # 5. Bicicletas (20 bicis)
        bicicletas = []
        # Intentamos obtener el estado correcto del Enum
        estado_inicial = getattr(EstadoBicicleta, 'disponible', 
                         getattr(EstadoBicicleta, 'disponibles', 
                         list(EstadoBicicleta)[0])) # Toma el primero si falla

        for i in range(1, 21):
            code = f"VLC{i:04d}"
            bici = Bicicleta(
                bicicleta_id=code,
                estacion_id=random.choice(estaciones).estacion_id,
                qr_code=f"QR-{code}",
                estado=estado_inicial
            )
            bicicletas.append(bici)
        db.add_all(bicicletas)
        db.commit()
        # 6. Placas
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

        # 7. TRAYECTOS (Clave para que la web cargue datos)
        # Generamos trayectos para TODOS los usuarios en el MES ACTUAL
        ahora = datetime.now(timezone.utc)
        primer_dia_mes = ahora.replace(day=1, hour=0, minute=0, second=0)
        
        for user in usuarios:
            # Cada usuario tendrá 2 trayectos este mes
            for j in range(2):
                inicio = primer_dia_mes + timedelta(days=j, hours=10)
                distancia = round(random.uniform(5.5, 12.0), 2)
                
                t = Trayecto(
                    trayecto_id=str(uuid.uuid4()),
                    usuario_id=user.usuario_id,
                    bicicleta_id=random.choice(bicicletas).bicicleta_id,
                    fecha_inicio=inicio,
                    fecha_fin=inicio + timedelta(minutes=45),
                    origen_estacion_id=random.choice(estaciones).estacion_id,
                    distancia_total=distancia
                )
                db.add(t)
        db.commit()

        # 8. Recompensas
        recompensas = [
            Recompensa(
                recompensa_id=str(uuid.uuid4()),  
                titulo="Café Gratis",
                descripcion="Canjea un café por 5km recorridos.",
                fecha_inicio=ahora - timedelta(days=1),
                fecha_fin=ahora + timedelta(days=30),
                criterio_num_km=5.0
            ),
            Recompensa(
                recompensa_id=str(uuid.uuid4()),  
                titulo="Descuento 10% McMenú",
                descripcion="Válido al completar 10km.",
                fecha_inicio=ahora - timedelta(days=1),
                fecha_fin=ahora + timedelta(days=30),
                criterio_num_km=10.0
            ),
            
            Recompensa(
                recompensa_id=str(uuid.uuid4()),  
                titulo="Recompensa prueba alta",
                descripcion="Recompensa prueba alta para testing.",
                fecha_inicio=ahora - timedelta(days=1),
                fecha_fin=ahora + timedelta(days=30),
                criterio_num_km=50.0
            ),
            
            
        ]
        db.add_all(recompensas)
        db.commit()

        # 9. RecompensasUsuario (Para que aparezcan en "Mis Recompensas")
        # Le damos al User0 una recompensa ya "desbloqueada"
        ru = RecompensaUsuario(
            usuario_id=usuarios[0].usuario_id,
            km_acumulados=25.0  # Simulamos que ya tiene km en su perfil
        )
        db.add(ru)
        db.commit()

        print(f"Seed finalizado con éxito.")
        print(f"Prueba con el usuario: {usuarios[0].correo} / Password123!")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()