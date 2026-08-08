from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from database import Base


# --- Enums ---

class TipoEquipo(str, enum.Enum):
    laptop = "Laptop"
    desktop = "Desktop"
    monitor = "Monitor"


class EstadoEquipo(str, enum.Enum):
    nuevo = "Nuevo"
    usado = "Usado"
    en_reparacion = "En reparación"


# --- Modelos ---

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    correo = Column(String(150), unique=True, index=True, nullable=False)
    area = Column(String(100), nullable=False)
    cargo = Column(String(100), nullable=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    # Relación: un usuario puede tener muchas asignaciones
    asignaciones = relationship("Asignacion", back_populates="usuario")


class Equipo(Base):
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False)        # Laptop / Desktop / Monitor
    marca = Column(String(100), nullable=False)
    modelo = Column(String(100), nullable=False)
    numero_serie = Column(String(100), unique=True, index=True, nullable=False)
    estado = Column(String(50), nullable=False)      # Nuevo / Usado / En reparación
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    # Relación: un equipo puede tener historial de asignaciones
    asignaciones = relationship("Asignacion", back_populates="equipo")


class Asignacion(Base):
    __tablename__ = "asignaciones"

    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer, ForeignKey("equipos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_asignacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_devolucion = Column(DateTime(timezone=True), nullable=True)
    activa = Column(Integer, default=1)  # 1 = activa, 0 = devuelta

    # Relaciones
    equipo = relationship("Equipo", back_populates="asignaciones")
    usuario = relationship("Usuario", back_populates="asignaciones")
