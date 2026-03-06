from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.medication import Medication
from app.schemas.medication import MedicationCreate, MedicationUpdate

def create_medication(db: Session, data: MedicationCreate) -> Medication:
    obj = Medication(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_medication(db: Session, medication_id: int) -> Optional[Medication]:
    return db.query(Medication).filter(Medication.id == medication_id).first()

def list_medications(db: Session, skip=0, limit=50) -> List[Medication]:
    return db.query(Medication).offset(skip).limit(limit).all()

def update_medication(db: Session, medication_id: int, data: MedicationUpdate) -> Optional[Medication]:
    obj = get_medication(db, medication_id)
    if not obj:
        return None
    upd = data.model_dump(exclude_unset=True)
    for k, v in upd.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

def delete_medication(db: Session, medication_id: int) -> bool:
    obj = get_medication(db, medication_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
