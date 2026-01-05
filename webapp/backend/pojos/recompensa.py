"""
@Author: Ariel Bejaran
@Date: 05/01/2026
@Description: POJO (Pydantic Model) para representar una Recompensa en la capa de lógica y API.
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional

class Recompensa(BaseModel):
    # Definimos los campos basándonos en tu lógica de "ingeniería inversa"
    recompensa_id: str  # En la DB es UUID, pero tu lógica lo convierte a str
    titulo: str
    descripcion: str
    fecha_inicio: datetime
    fecha_fin: datetime
    criterio_num_km: float

    # Esta configuración es CLAVE: permite que Pydantic lea datos directamente 
    # de objetos de SQLAlchemy (como recompensa_db) sin tener que hacer el dict manual.
    model_config = ConfigDict(from_attributes=True)