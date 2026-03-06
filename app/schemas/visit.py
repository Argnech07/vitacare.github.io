from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.validators import sanitize_optional_string

class VisitBase(BaseModel):
    patient_id: int = Field(..., gt=0, description="ID del paciente")
    doctor_id: int | None = Field(None, gt=0, description="ID del doctor")
    date_id: int | None = Field(None, description="ID de fecha")
    visit_ts: datetime = Field(..., description="Fecha y hora de la visita")
    reason: str | None = Field(None, min_length=3, max_length=2000, description="Motivo de la visita")
    exploration: str | None = Field(None, max_length=2000, description="Exploración física")
    therapeutic_plan: str | None = Field(None, max_length=2000, description="Plan terapéutico")

    @field_validator('reason', 'exploration', 'therapeutic_plan')
    @classmethod
    def sanitize_text_fields(cls, v: str | None) -> str | None:
        """Sanitiza campos de texto opcionales"""
        return sanitize_optional_string(v)

class VisitCreate(VisitBase):
    pass

class VisitUpdate(BaseModel):
    visit_ts: datetime | None = None
    reason: str | None = Field(None, min_length=3, max_length=2000)
    exploration: str | None = Field(None, max_length=2000)
    therapeutic_plan: str | None = Field(None, max_length=2000)
    user_id: int | None = Field(None, gt=0)
    date_id: int | None = None

    @field_validator('reason', 'exploration', 'therapeutic_plan')
    @classmethod
    def sanitize_text_fields(cls, v: str | None) -> str | None:
        """Sanitiza campos de texto opcionales"""
        return sanitize_optional_string(v)

class VisitOut(VisitBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Nuevo: Schema para diagnóstico enriquecido
class DiagnosisDetail(BaseModel):
    id: int
    code: str
    description: str
    diagnosis_description: Optional[str] = None
    secondary_diagnoses: List[str] = []

# Nuevo: Visit con diagnósticos incluidos
class VisitFull(VisitOut):
    diagnoses: List[DiagnosisDetail] = []

    