from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas, crud  # según tu estructura
from database import get_db

router = APIRouter()

# Listar todas las opciones de tipo incidente
@router.get("/tipo_incidente", response_model=list[schemas.Opcion])
def listar_tipo_incidente(db: Session = Depends(get_db)):
    return crud.get_all_tipo_incidente(db)

# Agregar tipo incidente si no existe
@router.post("/tipo_incidente", response_model=schemas.Opcion)
def agregar_tipo_incidente(opcion: schemas.OpcionCreate, db: Session = Depends(get_db)):
    res = crud.create_tipo_incidente(db, opcion.nombre.strip())
    if res is None:
        raise HTTPException(status_code=400, detail="La opción ya existe")
    return res

# Listar todas las fuentes de detección
@router.get("/fuentes_deteccion", response_model=list[schemas.Opcion])
def listar_fuentes_deteccion(db: Session = Depends(get_db)):
    return crud.get_all_fuentes_deteccion(db)

# Agregar fuente de detección si no existe
@router.post("/fuentes_deteccion", response_model=schemas.Opcion)
def agregar_fuentes_deteccion(opcion: schemas.OpcionCreate, db: Session = Depends(get_db)):
    res = crud.create_fuentes_deteccion(db, opcion.nombre.strip())
    if res is None:
        raise HTTPException(status_code=400, detail="La opción ya existe")
    return res