# models.py
from sqlalchemy import Column, Integer, String
from database import Base

class Threat(Base):
    __tablename__ = "threats"

    id = Column(Integer, primary_key=True, index=True)
    amenaza = Column(String, unique=True, index=True)  # <--- cambio aquí
    tipo_incidente = Column(String)
    severidad = Column(String)
    prioridad = Column(String)
    fuentes_deteccion = Column(String)

class TipoIncidente(Base):
    __tablename__ = "tipo_incidente"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)

class FuentesDeteccion(Base):
    __tablename__ = "fuentes_deteccion"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)