from __future__ import annotations

from typing import Optional
from datetime import date as date_type
from pydantic import BaseModel, Field, field_validator
from app.validators import sanitize_string, sanitize_optional_string

class PrescriptionBase(BaseModel):
    patient_id: int = Field(..., gt=0, description="ID del paciente")
    doctor_id: int = Field(..., gt=0, description="ID del doctor")
    license_number: str = Field(..., min_length=1, max_length=50, description="Número de licencia médica")
    specialty: str = Field(..., min_length=1, max_length=100, description="Especialidad médica")
    date: date_type = Field(..., description="Fecha de la prescripción")
    visit_diagnosis_id: Optional[int] = Field(None, description="ID del diagnóstico de la visita")
    notes: Optional[str] = Field(None, max_length=1000, description="Notas adicionales")

    @field_validator('license_number', 'specialty')
    @classmethod
    def sanitize_required_strings(cls, v: str) -> str:
        """Sanitiza campos obligatorios"""
        sanitized = sanitize_string(v)
        if not sanitized:
            raise ValueError("Este campo no puede estar vacío")
        return sanitized

    @field_validator('notes')
    @classmethod
    def sanitize_notes(cls, v: str | None) -> str | None:
        """Sanitiza notas opcionales"""
        return sanitize_optional_string(v)

class PrescriptionCreate(PrescriptionBase):
    pass

class PrescriptionUpdate(BaseModel):
    license_number: Optional[str] = Field(None, min_length=1, max_length=50)
    specialty: Optional[str] = Field(None, min_length=1, max_length=100)
    date: Optional[date_type] = None
    visit_diagnosis_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator('license_number', 'specialty')
    @classmethod
    def sanitize_optional_strings(cls, v: str | None) -> str | None:
        """Sanitiza campos opcionales que si están presentes deben tener valor"""
        if v is None:
            return None
        sanitized = sanitize_string(v)
        return sanitized if sanitized else None

    @field_validator('notes')
    @classmethod
    def sanitize_notes(cls, v: str | None) -> str | None:
        """Sanitiza notas opcionales"""
        return sanitize_optional_string(v)

class PrescriptionOut(PrescriptionBase):
    id: int
    pdf_path: Optional[str] = Field(None, description="Ruta del PDF guardado en el servidor")
    class Config:
        from_attributes = True
