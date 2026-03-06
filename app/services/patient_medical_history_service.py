# app/services/patient_medical_history_service.py
from typing import Optional
from sqlalchemy.orm import Session

from app.models.patient_medical_history import PatientMedicalHistory
from app.schemas.patient_medical_history import (
    PatientMedicalHistoryCreate,
    PatientMedicalHistoryUpdate,
)


def get_by_patient(db: Session, patient_id: int) -> Optional[PatientMedicalHistory]:
    return (
        db.query(PatientMedicalHistory)
        .filter(PatientMedicalHistory.patient_id == patient_id)
        .first()
    )


def create_for_patient(
    db: Session,
    patient_id: int,
    payload: PatientMedicalHistoryCreate,
) -> PatientMedicalHistory:
    history = PatientMedicalHistory(
        patient_id=patient_id,
        # Los submodelos Pydantic se convierten a dict para JSONB
        family_history=payload.family_history.model_dump()
        if payload.family_history
        else None,
        personal_habits=payload.personal_habits.model_dump()
        if payload.personal_habits
        else None,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def update_for_patient(
    db: Session,
    patient_id: int,
    payload: PatientMedicalHistoryUpdate,
) -> PatientMedicalHistory:
    history = get_by_patient(db, patient_id)
    if not history:
        # si no existe, creamos uno nuevo con los datos recibidos
        return create_for_patient(db, patient_id, PatientMedicalHistoryCreate(**payload.model_dump()))

    data = payload.model_dump(exclude_unset=True)

    if "family_history" in data and data["family_history"] is not None:
        history.family_history = data["family_history"]
    if "personal_habits" in data and data["personal_habits"] is not None:
        history.personal_habits = data["personal_habits"]

    db.commit()
    db.refresh(history)
    return history
