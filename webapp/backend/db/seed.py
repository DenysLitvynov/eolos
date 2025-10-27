"""
Autor: Denys Litvynov Lymanets
Fecha: 26-10-2025
Descripción: Script para insertar datos de prueba (seeds) en la BD. 
Ejecutar: python backend/db/seed.py
"""

# ---------------------------------------------------------

from .database import SessionLocal
from .models import Rol, Usuario, Mibisivalencia
from passlib.context import CryptContext
import uuid

# ---------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_data():
    
    from .database import Base, engine  # importa Base y engine aquí
    Base.metadata.create_all(bind=engine)  # <-- Esto crea todas las tablas si no existen

    db = SessionLocal()
    try:
        # Roles de prueba
        rol_usuario = Rol(nombre="usuario", descripcion="Usuario estándar")
        rol_admin = Rol(nombre="admin", descripcion="Administrador")
        db.add(rol_usuario)
        db.add(rol_admin)
        db.commit()
        
        # Mibisivalencia de prueba 
        carnet1 = Mibisivalencia(
            targeta_id=uuid.uuid4()
        )
        carnet2 = Mibisivalencia(
            targeta_id=uuid.uuid4()
        )
        db.add(carnet1)
        db.add(carnet2)
        db.commit()
        
        # Usuarios de prueba 
        hash1 = pwd_context.hash("password_segura1".encode("utf-8")[:72])
        usuario1 = Usuario(
            usuario_id=uuid.uuid4(),
            targeta_id=carnet1.targeta_id,  # Asocia a carnet1
            rol_id=1,  # usuario
            nombre="Usuario",
            apellido="Prueba1",
            correo="prueba1@fake.com",
            contrasena_hash=hash1
        )
        hash2 = pwd_context.hash("password_segura2".encode("utf-8")[:72])
        usuario2 = Usuario(
            usuario_id=uuid.uuid4(),
            targeta_id=None,  # Sin targeta
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
