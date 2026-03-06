from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.cie10 import CIE10Diagnosis
from app.models.visit import Visit
from app.models.visit_diagnosis import VisitDiagnosis
from app.schemas.visit import VisitCreate, VisitUpdate

def create_visit(db: Session, data: VisitCreate) -> Visit:
    visit = Visit(**data.model_dump())
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return visit

def get_visit(db: Session, visit_id: int) -> Optional[Visit]:
    return db.query(Visit).filter(Visit.id == visit_id).first()

def list_visits(db: Session, patient_id: Optional[int] = None, skip=0, limit=50) -> List[Visit]:
    query = db.query(Visit)
    if patient_id is not None:
        query = query.filter(Visit.patient_id == patient_id)
    return query.order_by(Visit.visit_ts.desc()).offset(skip).limit(limit).all()

def update_visit(db: Session, visit_id: int, data: VisitUpdate) -> Optional[Visit]:
    visit = get_visit(db, visit_id)
    if not visit:
        return None
    upd = data.model_dump(exclude_unset=True)
    for k, v in upd.items():
        setattr(visit, k, v)
    db.commit()
    db.refresh(visit)
    return visit

def delete_visit(db: Session, visit_id: int) -> bool:
    visit = get_visit(db, visit_id)
    if not visit:
        return False
    db.delete(visit)
    db.commit()
    return True

def get_visit_full(db: Session, visit_id: int) -> Optional[dict]:
    """
    Obtiene una visita completa con sus diagnósticos enriquecidos con CIE10
    """
    # Obtener la visita
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    
    if not visit:
        return None
    
    # Obtener diagnósticos de la visita
    visit_diagnoses = (
        db.query(VisitDiagnosis)
        .filter(VisitDiagnosis.visit_id == visit_id)
        .all()
    )
    
    # Enriquecer diagnósticos con información de CIE10
    diagnoses = []
    for vd in visit_diagnoses:
        # Buscar código principal en CIE10
        cie10 = db.query(CIE10Diagnosis).filter(
            CIE10Diagnosis.code == vd.primary_diagnosis
        ).first()
        
        diagnosis_data = {
            "id": vd.id,
            "code": vd.primary_diagnosis,
            "description": cie10.description if cie10 else "Descripción no disponible",
            "diagnosis_description": vd.diagnosis_description,
            "secondary_diagnoses": vd.secondary_diagnoses or []
        }
        diagnoses.append(diagnosis_data)
    
    # Construir respuesta completa
    result = {
        "id": visit.id,
        "patient_id": visit.patient_id,
        "doctor_id": visit.doctor_id,
        "date_id": visit.date_id,
        "visit_ts": visit.visit_ts,
        "reason": visit.reason,
        "exploration": visit.exploration,
        "therapeutic_plan": visit.therapeutic_plan,
        "created_at": visit.created_at,
        "updated_at": visit.updated_at,
        "diagnoses": diagnoses
    }
    
    return result