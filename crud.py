# crud.py
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import or_
import models, schemas

def get_threats(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    severidad: Optional[str] = None,
    prioridad: Optional[str] = None,
    tipo_incidente: Optional[str] = None,
    amenaza: Optional[str] = None
):
    query = db.query(models.Threat)

    if severidad:
        query = query.filter(models.Threat.severidad == severidad)
    if prioridad:
        query = query.filter(models.Threat.prioridad == prioridad)
    if tipo_incidente:
        query = query.filter(models.Threat.tipo_incidente == tipo_incidente)
    if amenaza:
        query = query.filter(models.Threat.amenaza.ilike(f"%{amenaza}%"))

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return {"total": total, "items": items}


def create_threat(db: Session, threat: schemas.ThreatCreate):
    amenaza_clean = threat.amenaza.strip()
    existing = db.query(models.Threat).filter(models.Threat.amenaza == amenaza_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail="La amenaza ya existe")
    
    threat_data = threat.dict()
    threat_data["amenaza"] = amenaza_clean
    threat_data["fuentes_deteccion"] = ",".join(threat_data["fuentes_deteccion"])
    
    db_threat = models.Threat(**threat_data)
    db.add(db_threat)
    db.commit()
    db.refresh(db_threat)
    return db_threat


def update_threat(db: Session, threat_id: int, threat: schemas.ThreatCreate):
    db_threat = db.query(models.Threat).filter(models.Threat.id == threat_id).first()
    if not db_threat:
        raise HTTPException(status_code=404, detail="Amenaza no encontrada")
    
    threat_data = threat.dict()
    # Aquí convierte la lista a string
    threat_data["fuentes_deteccion"] = ",".join(threat_data["fuentes_deteccion"])
    
    for key, value in threat_data.items():
        setattr(db_threat, key, value)
    
    db.commit()
    db.refresh(db_threat)
    return db_threat


def delete_threat(db: Session, threat_id: int):
    db_threat = db.query(models.Threat).filter(models.Threat.id == threat_id).first()
    if not db_threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    db.delete(db_threat)
    db.commit()
    return {"ok": True}


################

from sqlalchemy.orm import Session
from models import TipoIncidente, FuentesDeteccion

def get_all_tipo_incidente(db: Session):
    return db.query(TipoIncidente).all()

def get_all_fuentes_deteccion(db: Session):
    return db.query(FuentesDeteccion).all()

def create_tipo_incidente(db: Session, nombre: str):
    existente = db.query(TipoIncidente).filter(TipoIncidente.nombre == nombre).first()
    if existente:
        return None
    nueva = TipoIncidente(nombre=nombre)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def create_fuentes_deteccion(db: Session, nombre: str):
    existente = db.query(FuentesDeteccion).filter(FuentesDeteccion.nombre == nombre).first()
    if existente:
        return None
    nueva = FuentesDeteccion(nombre=nombre)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva
