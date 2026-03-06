from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.validators import sanitize_optional_string

class PrescribedItemBase(BaseModel):
    prescription_id: int = Field(..., gt=0, description="ID de la prescripción")

    medication_id: Optional[int] = Field(None, gt=0, description="ID del medicamento")
    medication_name: Optional[str] = Field(None, max_length=200, description="Nombre del medicamento")
    presentation: Optional[str] = Field(None, max_length=100, description="Presentación")
    route: Optional[str] = Field(None, max_length=50, description="Vía de administración")
    frequency_hours: Optional[int] = Field(None, ge=1, le=168, description="Frecuencia en horas")
    duration_days: Optional[int] = Field(None, ge=1, description="Duración en días")
    duration_unit: Optional[str] = Field(None, max_length=20, description="Unidad de duración: 'dias', 'semanas', 'meses'")
    dosage: Optional[str] = Field(None, max_length=100, description="Dosis")
    notes: Optional[str] = Field(None, max_length=500, description="Notas adicionales")

    @field_validator('medication_name', 'presentation', 'route', 'duration_unit', 'dosage', 'notes')
    @classmethod
    def sanitize_optional_strings(cls, v: str | None) -> str | None:
        """Sanitiza campos opcionales de tipo string"""
        return sanitize_optional_string(v)

    @field_validator('duration_unit')
    @classmethod
    def validate_duration_unit(cls, v: str | None) -> str | None:
        """Valida que la unidad de duración sea válida"""
        if v is None:
            return None
        v = sanitize_optional_string(v)
        if v and v.lower() not in ['dias', 'semanas', 'meses', 'día', 'días', 'semana', 'mes']:
            raise ValueError("La unidad de duración debe ser: 'dias', 'semanas' o 'meses'")
        return v.lower() if v else None

class PrescribedItemCreate(PrescribedItemBase):
    pass

class PrescribedItemUpdate(BaseModel):
    medication_id: Optional[int] = None
    medication_name: Optional[str] = None
    presentation: Optional[str] = None
    route: Optional[str] = None
    frequency_hours: Optional[int] = None
    duration_days: Optional[int] = None
    duration_unit: Optional[str] = None
    dosage: Optional[str] = None
    notes: Optional[str] = None

class PrescribedItemOut(PrescribedItemBase):
    id: int

    class Config:
        from_attributes = True
