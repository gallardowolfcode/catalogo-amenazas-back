# schemas.py
from pydantic import BaseModel
from typing import List

class ThreatBase(BaseModel):
    amenaza: str
    tipo_incidente: str
    severidad: str
    prioridad: str
    fuentes_deteccion: str

class ThreatCreate(ThreatBase):
    pass

class Threat(ThreatBase):
    id: int

    class Config:
        orm_mode = True

class PaginatedThreats(BaseModel):
    total: int
    items: List[Threat]
