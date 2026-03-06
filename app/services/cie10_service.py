from sqlalchemy.orm import Session
from typing import List
from app.models.cie10 import CIE10Diagnosis
from app.schemas.cie10 import CIE10Create

def create_cie10(db: Session, data: CIE10Create) -> CIE10Diagnosis:
    obj = CIE10Diagnosis(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_cie10(db: Session, skip=0, limit=50) -> List[CIE10Diagnosis]:
    return db.query(CIE10Diagnosis).order_by(CIE10Diagnosis.code.asc()).offset(skip).limit(limit).all()
