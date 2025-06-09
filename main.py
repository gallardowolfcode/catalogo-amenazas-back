# main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import models, schemas, crud
import io
import csv
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Permitir acceso desde cualquier frontend temporalmente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/threats", response_model=schemas.PaginatedThreats)
def read_threats(
    skip: int = 0,
    limit: int = 100,
    severidad: str | None = None,
    prioridad: str | None = None,
    tipo_incidente: str | None = None,
    db: Session = Depends(get_db)
):
    return crud.get_threats(
        db,
        skip=skip,
        limit=limit,
        severidad=severidad,
        prioridad=prioridad,
        tipo_incidente=tipo_incidente
    )

@app.post("/threats", response_model=schemas.Threat)
def create_threat(threat: schemas.ThreatCreate, db: Session = Depends(get_db)):
    return crud.create_threat(db=db, threat=threat)

@app.put("/threats/{threat_id}", response_model=schemas.Threat)
def update_threat(threat_id: int, threat: schemas.ThreatCreate, db: Session = Depends(get_db)):
    return crud.update_threat(db, threat_id, threat)

@app.delete("/threats/{threat_id}")
def delete_threat(threat_id: int, db: Session = Depends(get_db)):
    return crud.delete_threat(db, threat_id)

@app.get("/threats/export/csv")
def export_threats_csv(
    severidad: str | None = None,
    prioridad: str | None = None,
    tipo_incidente: str | None = None,
    db: Session = Depends(get_db)
):
    data = crud.get_threats(db, skip=0, limit=10_000, severidad=severidad, prioridad=prioridad, tipo_incidente=tipo_incidente)["items"]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Amenaza", "Tipo de Incidente", "Severidad", "Prioridad", "Fuentes de Detección"])
    for threat in data:
        writer.writerow([threat.amenaza, threat.tipo_incidente, threat.severidad, threat.prioridad, threat.fuentes_deteccion])

    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=amenazas.csv"})
