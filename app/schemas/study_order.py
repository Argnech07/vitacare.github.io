from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.study_item import StudyItemOut

class StudyOrderBase(BaseModel):
    patient_id: int
    doctor_id: int
    order_date: date | None = None

class StudyOrderCreate(StudyOrderBase):
    pass

class StudyOrderOut(StudyOrderBase):
    id: int
    class Config:
        from_attributes = True

# Schemas para información simplificada de paciente y médico
class PatientInfo(BaseModel):
    id: int
    full_name: str

class DoctorInfo(BaseModel):
    id: int
    full_name: str

# Nuevo: StudyOrder completo con toda la información necesaria para la card
class StudyOrderFull(StudyOrderOut):
    patient: PatientInfo
    doctor: DoctorInfo
    reason: Optional[str] = None
    items: List[StudyItemOut] = []