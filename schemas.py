from pydantic import BaseModel, validator
from typing import List, Optional

class ThreatBase(BaseModel):
    amenaza: str
    tipo_incidente: Optional[str]
    severidad: Optional[str]
    prioridad: Optional[str]
    fuentes_deteccion: List[str]

    @validator("fuentes_deteccion", pre=True)
    def split_fuentes(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        return v


class ThreatCreate(ThreatBase):
    amenaza: str
    tipo_incidente: str
    severidad: str
    prioridad: str
    fuentes_deteccion: List[str]

class Threat(BaseModel):
    id: int
    amenaza: str
    tipo_incidente: str
    severidad: str
    prioridad: str
    fuentes_deteccion: List[str]  # lista para la salida también

    class Config:
        orm_mode = True

    @validator("fuentes_deteccion", pre=True)
    def split_fuentes(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        return v


class PaginatedThreats(BaseModel):
    total: int
    items: List[Threat]

class OpcionBase(BaseModel):
    nombre: str

class OpcionCreate(OpcionBase):
    pass

class Opcion(OpcionBase):
    id: int

    class Config:
        orm_mode = True

class TipoIncidenteBase(BaseModel):
    nombre: str

class TipoIncidenteCreate(TipoIncidenteBase):
    pass

class TipoIncidente(TipoIncidenteBase):
    id: int

    class Config:
        from_attributes = True  # para Pydantic v2, antes orm_mode
