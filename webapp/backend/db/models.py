"""
Autor: Denys Litvynov Lymanets
Fecha: 15-11-2025
Descripción: Define todos los modelos de base de datos usando SQLAlchemy.
"""

# ---------------------------------------------------------

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    TIMESTAMP,
    ForeignKey,
    Boolean,
    Float,
    Numeric,
    Table,
    Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum as PyEnum

from .database import Base

# ---------------------------------------------------------

# Enums
class TipoMedidaEnum(PyEnum):
    pm2_5 = "pm2_5"
    pm10 = "pm10"
    co = "co"
    no2 = "no2"
    o3 = "o3"
    temperatura = "temperatura"
    humedad = "humedad"


class EstadoBicicleta(PyEnum):
    en_uso = "en_uso"
    estacionada = "estacionada"
    fuera_servicio = "fuera_servicio"
    mantenimiento = "mantenimiento"


class EstadoIncidencia(PyEnum):
    nuevo = "nuevo"
    en_proceso = "en_proceso"
    resuelto = "resuelto"
    cerrado = "cerrado"


class FuenteReporte(PyEnum):
    app = "app"
    web = "web"
    admin = "admin"

# ---------------------------------------------------------

# Tabla intermedia muchos a muchos usuarios ↔ roles
usuario_roles = Table(
    "usuario_roles",
    Base.metadata,
    Column("usuario_id", String(36), ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), primary_key=True),
    Column("rol_id", Integer, ForeignKey("roles.rol_id", ondelete="CASCADE"), primary_key=True)
)

# ---------------------------------------------------------

class Mibisivalencia(Base):
    __tablename__ = "mibisivalencia"
    targeta_id = Column(String(9), primary_key=True)  # 12345678A   

class Rol(Base):
    __tablename__ = "roles"
    
    rol_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text)

    usuarios = relationship("Usuario", secondary=usuario_roles, back_populates="roles")

class Usuario(Base):
    __tablename__ = "usuarios"
    
    usuario_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    targeta_id = Column(String(9), ForeignKey("mibisivalencia.targeta_id", ondelete="SET NULL"), nullable=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100))
    correo = Column(String(100), unique=True, nullable=False)
    contrasena_hash = Column(Text, nullable=False)
    
    # Relaciones
    roles = relationship("Rol", secondary=usuario_roles, back_populates="usuarios")
    mibisivalencia = relationship("Mibisivalencia", uselist=False)

# ---------------------------------------------------------

class Estacion(Base):
    __tablename__ = "estaciones"
    
    estacion_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    lat = Column(Numeric(9, 6), nullable=False)
    lon = Column(Numeric(9, 6), nullable=False)
    capacidad = Column(Integer, nullable=False)

    bicicletas = relationship("Bicicleta", back_populates="estacion")

class Bicicleta(Base):
    __tablename__ = "bicicletas"
    
    bicicleta_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    estacion_id = Column(Integer, ForeignKey("estaciones.estacion_id", ondelete="SET NULL"), nullable=True)
    qr_code = Column(String(100), unique=True, nullable=False)
    short_code = Column(String(20), unique=True, nullable=False)
    estado = Column(SQLEnum(EstadoBicicleta), default=EstadoBicicleta.estacionada, nullable=False)

    estacion = relationship("Estacion", back_populates="bicicletas")
    placa = relationship("PlacaSensores", uselist=False, back_populates="bicicleta")

class PlacaSensores(Base):
    __tablename__ = "placas_sensores"
    
    placa_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bicicleta_id = Column(String(36), ForeignKey("bicicletas.bicicleta_id", ondelete="CASCADE"), unique=True)
    estado = Column(String(50), nullable=False)  # activo / inactivo / etc.

    bicicleta = relationship("Bicicleta", back_populates="placa")

class Trayecto(Base):
    __tablename__ = "trayectos"
    
    trayecto_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), ForeignKey("usuarios.usuario_id"))
    bicicleta_id = Column(String(36), ForeignKey("bicicletas.bicicleta_id"))
    fecha_inicio = Column(TIMESTAMP(timezone=True), nullable=False)
    fecha_fin = Column(TIMESTAMP(timezone=True), nullable=True)
    origen_estacion_id = Column(Integer, ForeignKey("estaciones.estacion_id"))
    destino_estacion_id = Column(Integer, ForeignKey("estaciones.estacion_id"), nullable=True)
    distancia_total = Column(Float)

class Medida(Base):
    __tablename__ = "medidas"
    
    lectura_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    placa_id = Column(String(36), ForeignKey("placas_sensores.placa_id"))
    trayecto_id = Column(String(36), ForeignKey("trayectos.trayecto_id"))
    fecha_hora = Column(TIMESTAMP(timezone=True), nullable=False)
    tipo = Column(SQLEnum(TipoMedidaEnum), nullable=False)
    valor = Column(Float, nullable=False)
    lat = Column(Numeric(9,6), nullable=False)
    lon = Column(Numeric(9,6), nullable=False)

class Incidencia(Base):
    __tablename__ = "incidencias"
    
    incidencia_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), ForeignKey("usuarios.usuario_id"))
    bicicleta_id = Column(String(36), ForeignKey("bicicletas.bicicleta_id"), nullable=True)
    descripcion = Column(Text, nullable=False)
    fecha_reporte = Column(TIMESTAMP(timezone=True), server_default=func.now())
    estado = Column(SQLEnum(EstadoIncidencia), default=EstadoIncidencia.nuevo)
    fuente = Column(SQLEnum(FuenteReporte), nullable=False)

# ---------------------------------------------------------

# Tablas para auth con verificación
class PendingRegistration(Base):
    __tablename__ = "pending_registrations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100))
    correo = Column(String(100), unique=True, nullable=False)
    targeta_id = Column(String(36), ForeignKey("mibisivalencia.targeta_id", ondelete="SET NULL"), nullable=True)
    contrasena_hash = Column(Text, nullable=False)
    verification_code = Column(String(6), nullable=False)  # "637821"
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), nullable=False)
    token = Column(String(36), unique=True, nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

# ---------------------------------------------------------
