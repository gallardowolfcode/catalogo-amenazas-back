# import_excel.py
import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

# Crear las tablas si no existen
models.Base.metadata.create_all(bind=engine)

# Leer archivo Excel
df = pd.read_excel("Catalogo_Completo_de_Amenazas.xlsx")

# Insertar en DB evitando duplicados
db: Session = SessionLocal()
insertados = 0
omitidos = 0

for _, row in df.iterrows():
    # Buscar si ya existe por el campo 'amenaza'
    existente = db.query(models.Threat).filter(models.Threat.amenaza == row["Amenaza"]).first()
    if existente:
        omitidos += 1
        continue

    amenaza = models.Threat(
        amenaza=row["Amenaza"],
        tipo_incidente=row["Tipo de Incidente"],
        severidad=row["Severidad"],
        prioridad=row["Prioridad"],
        fuentes_deteccion=row["Fuentes de Detección"],
    )
    db.add(amenaza)
    insertados += 1

db.commit()
db.close()

print(f"✅ Importación completada: {insertados} nuevas amenazas insertadas, {omitidos} omitidas por duplicado.")

