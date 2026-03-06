from pydantic import BaseModel
from typing import List, Any

class VisitDiagnosisBase(BaseModel):
    visit_id: int
    primary_diagnosis: str
    secondary_diagnoses: List[str] | None = None
    diagnosis_description: str | None = None

class VisitDiagnosisCreate(VisitDiagnosisBase):
    pass

class VisitDiagnosisOut(VisitDiagnosisBase):
    id: int

    class Config:
        from_attributes = True
