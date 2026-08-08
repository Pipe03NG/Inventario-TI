from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ─────────────────────────────────────────
#  Schemas de Usuario
# ─────────────────────────────────────────

class UsuarioBase(BaseModel):
    nombre: str
    correo: str
    area: str
    cargo: str


class UsuarioCreate(UsuarioBase):
    pass


class UsuarioOut(UsuarioBase):
    id: int
    fecha_registro: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────
#  Schemas de Equipo
# ─────────────────────────────────────────

class EquipoBase(BaseModel):
    tipo: str
    marca: str
    modelo: str
    numero_serie: str
    estado: str


class EquipoCreate(EquipoBase):
    pass


class EquipoOut(EquipoBase):
    id: int
    fecha_registro: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────
#  Schemas de Asignación
# ─────────────────────────────────────────

class AsignacionCreate(BaseModel):
    equipo_id: int
    usuario_id: int


class AsignacionOut(BaseModel):
    id: int
    equipo_id: int
    usuario_id: int
    activa: int
    fecha_asignacion: Optional[datetime] = None
    fecha_devolucion: Optional[datetime] = None

    # Datos anidados para la vista del inventario
    equipo: Optional[EquipoOut] = None
    usuario: Optional[UsuarioOut] = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────
#  Schema combinado para el Dashboard
# ─────────────────────────────────────────

class InventarioItem(BaseModel):
    """Vista enriquecida de un equipo con su estado de asignación."""
    equipo: EquipoOut
    disponible: bool
    asignado_a: Optional[UsuarioOut] = None
    asignacion_id: Optional[int] = None

    model_config = {"from_attributes": True}
