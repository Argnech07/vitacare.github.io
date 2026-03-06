from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.schemas.visit_diagnosis import VisitDiagnosisCreate, VisitDiagnosisOut
from app.services import visit_diagnosis_service

router = APIRouter(prefix="/visit-diagnoses", tags=["visit-diagnoses"])

@router.post("/", response_model=VisitDiagnosisOut, status_code=status.HTTP_201_CREATED)
def create(payload: VisitDiagnosisCreate, db: Session = Depends(get_db)):
    return visit_diagnosis_service.create_visit_diagnosis(db, payload)

@router.get("/", response_model=List[VisitDiagnosisOut])
def all(visit_id: int = None, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return visit_diagnosis_service.list_visit_diagnoses(db, visit_id=visit_id, skip=skip, limit=limit)
