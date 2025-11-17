"""
Autor: Denys Litvynov Lymanets
Fecha: 26-10-2025
Descripción: Configura la conexión a la base de datos con SQLAlchemy.
"""

# ---------------------------------------------------------

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# ---------------------------------------------------------

# Carga variables de entorno desde .env
load_dotenv()

# URL de conexión
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ---------------------------------------------------------

def get_db():
    """
    Generador que provee una sesión de DB.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
