from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.patient_incapacity import PatientIncapacity
from app.schemas.patient_incapacity import PatientIncapacityCreate, PatientIncapacityUpdate


def list_by_patient(db: Session, patient_id: int, skip: int = 0, limit: int = 100) -> List[PatientIncapacity]:
    return (
        db.query(PatientIncapacity)
        .filter(PatientIncapacity.patient_id == patient_id)
        .order_by(desc(PatientIncapacity.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_for_patient(
    db: Session, patient_id: int, payload: PatientIncapacityCreate
) -> PatientIncapacity:
    obj = PatientIncapacity(
        patient_id=patient_id,
        incapacity_for=payload.incapacity_for,
        incapacity_type=payload.incapacity_type,
        reason=payload.reason,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def delete_for_patient(
    db: Session,
    *,
    patient_id: int,
    incapacity_id: int,
) -> bool:
    obj = (
        db.query(PatientIncapacity)
        .filter(PatientIncapacity.id == incapacity_id, PatientIncapacity.patient_id == patient_id)
        .first()
    )
    if not obj:
        return False

    db.delete(obj)
    db.commit()
    return True


def get_by_id(db: Session, incapacity_id: int) -> PatientIncapacity | None:
    return db.query(PatientIncapacity).filter(PatientIncapacity.id == incapacity_id).first()


def update_for_patient(
    db: Session,
    *,
    patient_id: int,
    incapacity_id: int,
    payload: PatientIncapacityUpdate,
) -> PatientIncapacity | None:
    obj = (
        db.query(PatientIncapacity)
        .filter(PatientIncapacity.id == incapacity_id, PatientIncapacity.patient_id == patient_id)
        .first()
    )
    if not obj:
        return None

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(obj, field, value)

    db.commit()
    db.refresh(obj)
    return obj
