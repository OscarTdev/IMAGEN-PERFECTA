from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.schemas.anomalia import AnomaliaResponse, AnomaliaRevision
from app.services import anomalia_service
from app.models.anomalia import Anomalia
from app.core import config as cfg

router = APIRouter(prefix="/api", tags=["Seguridad"])

@router.get("/anomalias", response_model=List[AnomaliaResponse])
def listar(tipo: Optional[str] = None, estado_revision: Optional[str] = None,
           db: Session = Depends(get_db)):
    return anomalia_service.listar(db, tipo, estado_revision)

@router.patch("/anomalias/{id}", response_model=AnomaliaResponse)
def revisar(id: int, data: AnomaliaRevision, db: Session = Depends(get_db)):
    a = db.query(Anomalia).filter(Anomalia.id == id).first()
    if not a:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Anomalía no encontrada")
    a.estado_revision = data.estado_revision
    db.commit()
    db.refresh(a)
    return a

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    return anomalia_service.resumen_dashboard(db)

@router.get("/config")
def get_config():
    return cfg.get_config()

@router.put("/config")
def set_config(payload: dict):
    return cfg.set_config(
        ventana_segundos=payload.get("ventana_segundos"),
        umbral=payload.get("umbral_transacciones"),
        ventanas_turno=payload.get("ventanas_turno") or payload.get("limites_turno"),
    )
