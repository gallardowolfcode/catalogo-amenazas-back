# main.py
from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse, JSONResponse
import models, schemas, crud
import io
import csv
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from routers import opciones 
from fastapi.exceptions import RequestValidationError


models.Base.metadata.create_all(bind=engine)


app = FastAPI()
app.include_router(opciones.router, prefix="/options", tags=["Opciones"])

# Agrega esto:
origins = [
    "https://catalogoamenazas.netlify.app",  # Tu frontend en Netlify
    "http://localhost:3000"  # Opcional, si usas React local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permitir solo estos orígenes
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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("Validation error:", exc.errors())
    print("Request body:", exc.body)
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.get("/threats", response_model=schemas.PaginatedThreats)
def read_threats(
    skip: int = 0,
    limit: int = 100,
    severidad: Optional[str] = None,
    prioridad: Optional[str] = None,
    tipo_incidente: Optional[str] = None,
    amenaza: Optional[str] = None,
    db: Session = Depends(get_db)
) -> schemas.PaginatedThreats:
    return crud.get_threats(
        db,
        skip=skip,
        limit=limit,
        severidad=severidad,
        prioridad=prioridad,
        tipo_incidente=tipo_incidente,
        amenaza=amenaza
    )

@app.post("/threats", response_model=schemas.Threat)
def create_threat(threat: schemas.ThreatCreate, db: Session = Depends(get_db)):
    amenaza_clean = threat.amenaza.strip()
    existing = db.query(models.Threat).filter(models.Threat.amenaza == amenaza_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail="La amenaza ya existe")
    
    # Verificar o crear tipo_incidente
    tipo_incidente_obj = db.query(models.TipoIncidente).filter(models.TipoIncidente.nombre == threat.tipo_incidente).first()
    if not tipo_incidente_obj:
        tipo_incidente_obj = models.TipoIncidente(nombre=threat.tipo_incidente)
        db.add(tipo_incidente_obj)
        db.commit()
        db.refresh(tipo_incidente_obj)
    
    threat_data = threat.dict()
    threat_data["amenaza"] = amenaza_clean
    threat_data["fuentes_deteccion"] = ",".join(threat_data["fuentes_deteccion"])
    # Guardar el nombre o la referencia del tipo incidente (según tu diseño)
    threat_data["tipo_incidente"] = tipo_incidente_obj.nombre
    
    db_threat = models.Threat(**threat_data)
    db.add(db_threat)
    db.commit()
    db.refresh(db_threat)
    return db_threat


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

    output = io.StringIO(newline='', encoding='utf-8-sig')  # <- Aquí está el cambio clave
    writer = csv.writer(output)
    writer.writerow(["Amenaza", "Tipo de Incidente", "Severidad", "Prioridad", "Fuentes de Detección"])
    for threat in data:
        writer.writerow([
            threat.amenaza,
            threat.tipo_incidente,
            threat.severidad,
            threat.prioridad,
            threat.fuentes_deteccion
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=amenazas.csv"}
    )