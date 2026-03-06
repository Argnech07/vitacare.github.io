from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.validators import sanitize_optional_string, sanitize_string


class PatientIncapacityBase(BaseModel):
    incapacity_type: str = Field(..., max_length=100)
    reason: Optional[str] = Field(None, max_length=2000)

    @field_validator("incapacity_type")
    @classmethod
    def _sanitize_type(cls, v: str) -> str:
        v = sanitize_string(v)
        if not v:
            raise ValueError("El tipo de incapacidad es obligatorio")
        return v

    @field_validator("reason")
    @classmethod
    def _sanitize_reason(cls, v: Optional[str]) -> Optional[str]:
        return sanitize_optional_string(v)


class PatientIncapacityCreate(PatientIncapacityBase):
    incapacity_for: str = Field(..., max_length=50)

    @field_validator("incapacity_for")
    @classmethod
    def _sanitize_for(cls, v: str) -> str:
        v = sanitize_string(v)
        if not v:
            raise ValueError("El campo 'Incapacidad por' es obligatorio")
        return v


class PatientIncapacityUpdate(BaseModel):
    incapacity_for: Optional[str] = Field(None, max_length=50)
    incapacity_type: Optional[str] = Field(None, max_length=100)
    reason: Optional[str] = Field(None, max_length=2000)

    @field_validator("incapacity_for")
    @classmethod
    def _sanitize_for(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = sanitize_string(v)
        if not v:
            raise ValueError("El campo 'Incapacidad por' es obligatorio")
        return v

    @field_validator("incapacity_type")
    @classmethod
    def _sanitize_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = sanitize_string(v)
        if not v:
            raise ValueError("El tipo de incapacidad es obligatorio")
        return v

    @field_validator("reason")
    @classmethod
    def _sanitize_reason(cls, v: Optional[str]) -> Optional[str]:
        return sanitize_optional_string(v)


class PatientIncapacityOut(PatientIncapacityBase):
    id: int
    patient_id: int
    incapacity_for: Optional[str] = Field(None, max_length=50)
    created_at: datetime

    class Config:
        from_attributes = True
