from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.db import get_db
from app.schemas.patient_medical_history import (
    PatientMedicalHistoryOut,
    PatientMedicalHistoryCreate,
    PatientMedicalHistoryUpdate,
)
from app.services import patient_medical_history_service

router = APIRouter(
    prefix="/patients/{patient_id}/medical-history",
    tags=["medical_history"],
)


@router.get("/", response_model=Optional[PatientMedicalHistoryOut])
def get_medical_history(patient_id: int, db: Session = Depends(get_db)):
    history = patient_medical_history_service.get_by_patient(db, patient_id)
    if not history:
        return None
    return history

@router.post("/", response_model=PatientMedicalHistoryOut, status_code=status.HTTP_201_CREATED)
def create_medical_history(
    patient_id: int,
    payload: PatientMedicalHistoryCreate,
    db: Session = Depends(get_db),
):
    history = patient_medical_history_service.get_by_patient(db, patient_id)
    if history:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medical history already exists for this patient",
        )
    history = patient_medical_history_service.create_for_patient(db, patient_id, payload)
    return history


@router.put("/", response_model=PatientMedicalHistoryOut)
def upsert_medical_history(
    patient_id: int,
    payload: PatientMedicalHistoryUpdate,
    db: Session = Depends(get_db),
):
    history = patient_medical_history_service.update_for_patient(db, patient_id, payload)
    return history

@router.patch("/", response_model=PatientMedicalHistoryOut)
def partial_update_medical_history(
    patient_id: int,
    payload: dict[str, Any],
    db: Session = Depends(get_db),
):
    
    history = patient_medical_history_service.get_by_patient(db, patient_id)
    
    if not history:
        # Crear si no existe
        return patient_medical_history_service.create_for_patient(
            db, patient_id, PatientMedicalHistoryCreate(**payload)
        )
    
    # Actualizar parcialmente
    if "family_history" in payload:
        current_fh = history.family_history or {}
        history.family_history = {**current_fh, **payload["family_history"]}
    
    if "personal_habits" in payload:
        current_ph = history.personal_habits or {}
        history.personal_habits = {**current_ph, **payload["personal_habits"]}
    
    db.commit()
    db.refresh(history)
    return history