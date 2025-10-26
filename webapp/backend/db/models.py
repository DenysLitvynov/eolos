"""
Autor: Denys Litvynov Lymanets
Fecha: 26-10-2025
Descripción: Define los modelos de base de datos usando SQLAlchemy. Representan las tablas.
"""

# ---------------------------------------------------------

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .database import Base

# ---------------------------------------------------------

class Mibisivalencia(Base):
    __tablename__ = "mibisivalencia"
    
    targeta_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

# ---------------------------------------------------------

class Rol(Base):
    __tablename__ = "roles"
    
    rol_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text)

# ---------------------------------------------------------

class Usuario(Base):
    __tablename__ = "usuarios"
    
    usuario_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    targeta_id = Column(UUID(as_uuid=True), ForeignKey("mibisivalencia.targeta_id", ondelete="SET NULL"))
    rol_id = Column(Integer, ForeignKey("roles.rol_id", ondelete="SET NULL"))
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100))
    correo = Column(String(100), unique=True, nullable=False)
    contrasena_hash = Column(Text, nullable=False)
    fecha_registro = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    mibisivalencia = relationship("Mibisivalencia")
    rol = relationship("Rol")

# ---------------------------------------------------------

