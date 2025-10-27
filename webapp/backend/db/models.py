"""
Autor: Denys Litvynov Lymanets
Fecha: 27-10-2025
Descripción: Define los modelos de base de datos usando SQLAlchemy. Representan las tablas.
"""

# ---------------------------------------------------------

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# ---------------------------------------------------------

class Mibisivalencia(Base):
    __tablename__ = "mibisivalencia"
    
    targeta_id = Column(String(9), primary_key=True)  # Formato tipo DNI (ej. 12345678A)

# ---------------------------------------------------------

class Rol(Base):
    __tablename__ = "roles"
    
    rol_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text)

# ---------------------------------------------------------

class Usuario(Base):
    __tablename__ = "usuarios"
    
    usuario_id = Column(String(36), primary_key=True)  # Mantiene UUID como string para usuario_id
    targeta_id = Column(String(9), ForeignKey("mibisivalencia.targeta_id", ondelete="SET NULL"))  # Cambiado a String(9)
    rol_id = Column(Integer, ForeignKey("roles.rol_id", ondelete="SET NULL"))
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100))
    correo = Column(String(100), unique=True, nullable=False)
    contrasena_hash = Column(Text, nullable=False)
    
    mibisivalencia = relationship("Mibisivalencia")
    rol = relationship("Rol")

# ---------------------------------------------------------
