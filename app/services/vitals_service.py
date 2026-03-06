from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.vitals import Vitals
from app.schemas.vitals import VitalsCreate, VitalsUpdate


def get_latest_vitals(db: Session, patient_id: int) -> Optional[Vitals]:
    return (
        db.query(Vitals)
        .filter(Vitals.patient_id == patient_id)
        .order_by(desc(Vitals.taken_at))  # taken_at, no measured_at
        .first()
    )


def list_vitals(
    db: Session,
    patient_id: int,
    skip: int = 0,
    limit: int = 50,
) -> List[Vitals]:
    return (
        db.query(Vitals)
        .filter(Vitals.patient_id == patient_id)
        .order_by(desc(Vitals.taken_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_vitals(
    db: Session,
    patient_id: int,
    payload: VitalsCreate,
) -> Vitals:
    vitals = Vitals(
        patient_id=patient_id,
        **payload.model_dump(),  # si Pydantic v2
        # **payload.dict(),      # si Pydantic v1
    )
    db.add(vitals)
    db.commit()
    db.refresh(vitals)
    return vitals


def update_vitals(
    db: Session,
    vitals_id: int,
    payload: VitalsUpdate,
) -> Optional[Vitals]:
    vitals = db.query(Vitals).filter(Vitals.id == vitals_id).first()
    if not vitals:
        return None

    for field, value in payload.model_dump(exclude_unset=True).items():  # o dict()
        setattr(vitals, field, value)

    db.commit()
    db.refresh(vitals)
    return vitals
