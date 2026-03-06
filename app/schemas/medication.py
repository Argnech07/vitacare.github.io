from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.validators import sanitize_string, sanitize_optional_string

class MedicationBase(BaseModel):
    generic_name: str = Field(..., min_length=1, max_length=200, description="Nombre genérico del medicamento")
    brand_name: Optional[str] = Field(None, max_length=200, description="Nombre comercial del medicamento")
    form: Optional[str] = Field(None, max_length=50, description="Forma farmacéutica")
    strength: Optional[str] = Field(None, max_length=50, description="Concentración o potencia")

    @field_validator('generic_name')
    @classmethod
    def sanitize_generic_name(cls, v: str) -> str:
        """Sanitiza nombre genérico obligatorio"""
        sanitized = sanitize_string(v)
        if not sanitized:
            raise ValueError("El nombre genérico no puede estar vacío")
        return sanitized

    @field_validator('brand_name', 'form', 'strength')
    @classmethod
    def sanitize_optional_strings(cls, v: str | None) -> str | None:
        """Sanitiza campos opcionales"""
        return sanitize_optional_string(v)

class MedicationCreate(MedicationBase):
    pass

class MedicationUpdate(BaseModel):
    generic_name: Optional[str] = Field(None, min_length=1, max_length=200)
    brand_name: Optional[str] = Field(None, max_length=200)
    form: Optional[str] = Field(None, max_length=50)
    strength: Optional[str] = Field(None, max_length=50)

    @field_validator('generic_name')
    @classmethod
    def sanitize_generic_name(cls, v: str | None) -> str | None:
        """Sanitiza nombre genérico opcional que si está presente debe tener valor"""
        if v is None:
            return None
        sanitized = sanitize_string(v)
        return sanitized if sanitized else None

    @field_validator('brand_name', 'form', 'strength')
    @classmethod
    def sanitize_optional_strings(cls, v: str | None) -> str | None:
        """Sanitiza campos opcionales"""
        return sanitize_optional_string(v)

class MedicationOut(MedicationBase):
    id: int
    class Config:
        from_attributes = True
