from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.visit_diagnosis import VisitDiagnosis
from app.schemas.visit_diagnosis import VisitDiagnosisCreate

def create_visit_diagnosis(db: Session, data: VisitDiagnosisCreate) -> VisitDiagnosis:
    obj = VisitDiagnosis(
        visit_id=data.visit_id,
        primary_diagnosis=data.primary_diagnosis,
        secondary_diagnoses=data.secondary_diagnoses,
        diagnosis_description=data.diagnosis_description,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_visit_diagnoses(db: Session, visit_id: int = None, skip=0, limit=50) -> List[VisitDiagnosis]:
    query = db.query(VisitDiagnosis)
    if visit_id:
        query = query.filter(VisitDiagnosis.visit_id == visit_id)
    return query.offset(skip).limit(limit).all()
