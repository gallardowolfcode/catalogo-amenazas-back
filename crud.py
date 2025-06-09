# crud.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
import models, schemas

def get_threats(db: Session, skip=0, limit=100, severidad=None, prioridad=None, tipo_incidente=None):
    query = db.query(models.Threat)

    if severidad:
        query = query.filter(models.Threat.severidad.ilike(f"%{severidad}%"))
    if prioridad:
        query = query.filter(models.Threat.prioridad.ilike(f"%{prioridad}%"))
    if tipo_incidente:
        query = query.filter(models.Threat.tipo_incidente.ilike(f"%{tipo_incidente}%"))

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return {"total": total, "items": items}


def create_threat(db: Session, threat: schemas.ThreatCreate):
    db_threat = models.Threat(**threat.dict())
    db.add(db_threat)
    db.commit()
    db.refresh(db_threat)
    return db_threat

def update_threat(db: Session, threat_id: int, threat: schemas.ThreatCreate):
    db_threat = db.query(models.Threat).filter(models.Threat.id == threat_id).first()
    if not db_threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    for key, value in threat.dict().items():
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
