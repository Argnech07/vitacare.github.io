from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.schemas.prescription import PrescriptionOut
from app.schemas.study_order import StudyOrderOut
from app.schemas.visit import VisitOut
from app.schemas.visit_diagnosis import VisitDiagnosisOut

class AttentionBase(BaseModel):
    visit_id: Optional[int] = None
    prescription_id: Optional[int] = None
    study_order_id: Optional[int] = None
    doctor_id: Optional[int] = None
    patient_id: Optional[int] = None

class AttentionCreate(AttentionBase):
    pass

class AttentionUpdate(BaseModel):
    visit_id: Optional[int] = None
    prescription_id: Optional[int] = None
    study_order_id: Optional[int] = None
    doctor_id: Optional[int] = None
    patient_id: Optional[int] = None

class AttentionOut(AttentionBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class AttentionFull(AttentionOut):
    visit: Optional[VisitOut] = None
    prescription: Optional[PrescriptionOut] = None
    study_order: Optional[StudyOrderOut] = None
    diagnoses: List[VisitDiagnosisOut] = []  