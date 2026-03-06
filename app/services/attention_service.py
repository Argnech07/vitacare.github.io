from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.attention import Attention
from app.models.prescribed_item import PrescribedItem
from app.schemas.attention import AttentionCreate, AttentionUpdate

def create_attention(db: Session, data: AttentionCreate) -> Attention:
    obj = Attention(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_attention(db: Session, attention_id: int) -> Optional[Attention]:
    return db.query(Attention).filter(Attention.id == attention_id).first()

def list_attentions(db: Session, doctor_id: Optional[int] = None, patient_id: Optional[int] = None, skip=0, limit=50) -> List[Attention]:
    query = db.query(Attention)
    if doctor_id:
        query = query.filter(Attention.doctor_id == doctor_id)
    if patient_id:
        query = query.filter(Attention.patient_id == patient_id)
    query = query.order_by(Attention.created_at.desc(), Attention.id.desc())
    return query.offset(skip).limit(limit).all()

def update_attention(db: Session, attention_id: int, data: AttentionUpdate) -> Optional[Attention]:
    obj = get_attention(db, attention_id)
    if not obj:
        return None
    upd = data.model_dump(exclude_unset=True)
    
    # Regla: Una atención solo puede tener una prescripción
    # Si la atención ya tiene una prescripción asociada, mantenerla
    # Solo permitir cambiar si se envía explícitamente None para desasociar
    if 'prescription_id' in upd:
        if obj.prescription_id is not None:
            # Si ya existe una prescripción asociada a esta atención
            if upd['prescription_id'] is not None:
                # No permitir cambiar a otra prescripción diferente
                # Mantener la prescripción actual para evitar duplicados
                upd.pop('prescription_id')
            # Si upd['prescription_id'] es None, permitir la desasociación
        # Si obj.prescription_id is None y se envía un prescription_id, permitir la asociación inicial
    
    for k, v in upd.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

def delete_attention(db: Session, attention_id: int) -> bool:
    obj = get_attention(db, attention_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
