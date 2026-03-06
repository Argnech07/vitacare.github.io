from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.prescription import Prescription
from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate

def create_prescription(db: Session, data: PrescriptionCreate) -> Prescription:
    # Verificar si ya existe una prescripción con los mismos datos clave
    # para evitar duplicados cuando se hace clic múltiples veces
    existing_query = db.query(Prescription).filter(
        Prescription.patient_id == data.patient_id,
        Prescription.doctor_id == data.doctor_id,
        Prescription.date == data.date
    )
    
    # Filtrar por visit_diagnosis_id (puede ser None)
    if data.visit_diagnosis_id is not None:
        existing = existing_query.filter(
            Prescription.visit_diagnosis_id == data.visit_diagnosis_id
        ).first()
    else:
        existing = existing_query.filter(
            Prescription.visit_diagnosis_id.is_(None)
        ).first()
    
    # Si existe una prescripción con los mismos datos, retornar la existente
    # en lugar de crear una nueva para evitar duplicados
    # Nota: La lógica en update_attention previene que se asocie una nueva
    # prescripción si la atención ya tiene una asociada
    if existing:
        return existing
    
    # Si no existe, crear una nueva
    obj = Prescription(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_prescription(db: Session, prescription_id: int) -> Optional[Prescription]:
    return db.query(Prescription).filter(Prescription.id == prescription_id).first()

def list_prescriptions(db: Session, patient_id: Optional[int] = None, doctor_id: Optional[int] = None, skip=0, limit=50) -> List[Prescription]:
    query = db.query(Prescription)
    if patient_id:
        query = query.filter(Prescription.patient_id == patient_id)
    if doctor_id:
        query = query.filter(Prescription.doctor_id == doctor_id)
    return query.offset(skip).limit(limit).all()

def update_prescription(db: Session, prescription_id: int, data: PrescriptionUpdate) -> Optional[Prescription]:
    obj = get_prescription(db, prescription_id)
    if not obj:
        return None
    upd = data.model_dump(exclude_unset=True)
    for k, v in upd.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

def delete_prescription(db: Session, prescription_id: int) -> bool:
    obj = get_prescription(db, prescription_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def update_prescription_pdf_path(db: Session, prescription_id: int, pdf_path: str) -> Optional[Prescription]:
    """Actualiza la ruta del PDF guardado para una receta"""
    obj = get_prescription(db, prescription_id)
    if not obj:
        return None
    obj.pdf_path = pdf_path
    db.commit()
    db.refresh(obj)
    return obj


def verify_prescription_by_id(db: Session, prescription_id: int) -> Optional[dict]:
    """Verificar una receta por ID y retornar todos los detalles para validación QR"""
    from app.models.patient import Patient
    from app.models.doctor import Doctor
    from app.models.prescribed_item import PrescribedItem
    from app.models.visit_diagnosis import VisitDiagnosis
    
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        return None
    
    # Cargar relaciones
    patient = db.query(Patient).filter(Patient.id == prescription.patient_id).first()
    doctor = db.query(Doctor).filter(Doctor.id == prescription.doctor_id).first()
    items = db.query(PrescribedItem).filter(PrescribedItem.prescription_id == prescription.id).all()
    diagnosis = db.query(VisitDiagnosis).filter(VisitDiagnosis.id == prescription.visit_diagnosis_id).first()
    
    return {
        "id": prescription.id,
        "folio": f"RC-{prescription.date.year}-{str(prescription.id).zfill(3)}",
        "date": prescription.date.isoformat() if prescription.date else None,
        "license_number": prescription.license_number,
        "specialty": prescription.specialty,
        "notes": prescription.notes,
        "patient": {
            "id": patient.id if patient else None,
            "full_name": f"{patient.first_name} {patient.middle_name or ''} {patient.last_name}".strip() if patient else None,
            "birth_date": patient.birth_date.isoformat() if patient and patient.birth_date else None,
            "gender": patient.gender if patient else None,
        } if patient else None,
        "doctor": {
            "id": doctor.id if doctor else None,
            "full_name": f"{doctor.first_name} {doctor.middle_name or ''} {doctor.last_name}".strip() if doctor else None,
        } if doctor else None,
        "medications": [
            {
                "name": item.medication_name,
                "presentation": item.presentation,
                "dosage": item.dosage,
                "frequency_hours": item.frequency_hours,
                "duration_days": item.duration_days,
                "route": item.route,
                "notes": item.notes,
            }
            for item in items
        ],
        "diagnosis": {
            "primary": diagnosis.primary_diagnosis if diagnosis else None,
            "secondary": diagnosis.secondary_diagnoses if diagnosis else None,
        } if diagnosis else None,
    }
