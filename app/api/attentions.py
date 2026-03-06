from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.schemas.attention import AttentionCreate, AttentionUpdate, AttentionOut
from app.services import attention_service
from app.models.attention import Attention
from app.models.prescription import Prescription
from app.models.prescribed_item import PrescribedItem
from app.models.medication import Medication
from app.models.study_order import StudyOrder
from app.models.visit import Visit

router = APIRouter(prefix="/attentions", tags=["attentions"])

@router.post("/", response_model=AttentionOut, status_code=status.HTTP_201_CREATED)
def create(payload: AttentionCreate, db: Session = Depends(get_db)):
    return attention_service.create_attention(db, payload)

@router.get("/", response_model=List[AttentionOut])
def all(
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return attention_service.list_attentions(db, doctor_id=doctor_id, patient_id=patient_id, skip=skip, limit=limit)

@router.get("/{attention_id}", response_model=AttentionOut)
def get_one(attention_id: int, db: Session = Depends(get_db)):
    obj = attention_service.get_attention(db, attention_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Attention not found")
    return obj

@router.put("/{attention_id}", response_model=AttentionOut)
def update(attention_id: int, payload: AttentionUpdate, db: Session = Depends(get_db)):
    obj = attention_service.update_attention(db, attention_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Attention not found")
    return obj

@router.delete("/{attention_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(attention_id: int, db: Session = Depends(get_db)):
    deleted = attention_service.delete_attention(db, attention_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Attention not found")

@router.get("/{attention_id}/full")
def get_attention_full(attention_id: int, db: Session = Depends(get_db)):
    attention = db.query(Attention).filter_by(id=attention_id).first()
    if not attention:
        raise HTTPException(status_code=404, detail="Attention not found")

    # Relaciona la visita
    visit = db.query(Visit).filter_by(id=attention.visit_id).first() if attention.visit_id else None

    # Receta y medicamentos completos
    prescription = db.query(Prescription).filter_by(id=attention.prescription_id).first() if attention.prescription_id else None
    prescribed_items = []
    if prescription:
        items = (
            db.query(PrescribedItem, Medication)
            .join(Medication, PrescribedItem.medication_id == Medication.id)
            .filter(PrescribedItem.prescription_id == prescription.id)
            .all()
        )
        prescribed_items = [
            {
                "id": i.PrescribedItem.id,
                "medication": {
                    "id": i.Medication.id,
                    "generic_name": i.Medication.generic_name,
                    "brand_name": i.Medication.brand_name,
                    "form": i.Medication.form,
                    "strength": i.Medication.strength,
                },
                "frequency_hours": i.PrescribedItem.frequency_hours,
                "duration_days": i.PrescribedItem.duration_days,
                "dosage": i.PrescribedItem.dosage,
                "notes": i.PrescribedItem.notes,
            }
            for i in items
        ]

    # Estudio ligado (si existe)
    study_order = db.query(StudyOrder).filter_by(id=attention.study_order_id).first() if attention.study_order_id else None

    return {
        "attention": {
            "id": attention.id,
            "visit_id": attention.visit_id,
            "prescription_id": attention.prescription_id,
            "study_order_id": attention.study_order_id,
            "doctor_id": attention.doctor_id,
            "patient_id": attention.patient_id,
            "created_at": attention.created_at,
        },
        "visit": visit.__dict__ if visit else None,
        "prescription": {
            "id": prescription.id,
            "date": prescription.date,
            "notes": prescription.notes,
        } if prescription else None,
        "prescribed_items": prescribed_items,
        "study_order": study_order.__dict__ if study_order else None
    }
