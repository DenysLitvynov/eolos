"""
Autor: Denys Litvynov Lymanets
Fecha: 27-10-2025
Descripción: Script para insertar datos de prueba (seeds) en la BD. 
Ejecutar: python backend/db/seed.py
"""

# ---------------------------------------------------------

from .database import SessionLocal, Base, engine
from .models import Rol, Usuario, Mibisivalencia
from passlib.context import CryptContext
import uuid

# ---------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_data():
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Roles de prueba
        rol_usuario = Rol(nombre="usuario", descripcion="Usuario estándar")
        rol_admin = Rol(nombre="admin", descripcion="Administrador")
        db.add(rol_usuario)
        db.add(rol_admin)
        db.commit()
        
        # Mibisivalencia de prueba (carnets con formato DNI)
        carnet1 = Mibisivalencia(targeta_id="12345678A")
        carnet2 = Mibisivalencia(targeta_id="87654321B")
        db.add(carnet1)
        db.add(carnet2)
        db.commit()
        
        # Usuarios de prueba
        hash1 = pwd_context.hash("password1".encode("utf-8")[:72])
        usuario1 = Usuario(
            usuario_id=str(uuid.uuid4()),  # UUID como string
            targeta_id="12345678A",  # Asocia a carnet1
            rol_id=1,  # usuario
            nombre="Usuario",
            apellido="Prueba1",
            correo="prueba1@fake.com",
            contrasena_hash=hash1
        )
        hash2 = pwd_context.hash("password2".encode("utf-8")[:72])
        usuario2 = Usuario(
            usuario_id=str(uuid.uuid4()),
            targeta_id=None,  # Sin carnet
            rol_id=2,  # admin
            nombre="Admin",
            apellido="Prueba2",
            correo="prueba2@fake.com",
            contrasena_hash=hash2
        )
        db.add(usuario1)
        db.add(usuario2)
        db.commit()
        print("Datos de prueba insertados exitosamente.")
    except Exception as e:
        db.rollback()
        print(f"Error insertando datos: {e}")
    finally:
        db.close()

# ---------------------------------------------------------

if __name__ == "__main__":
    seed_data()

# ---------------------------------------------------------
