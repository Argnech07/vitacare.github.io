from datetime import date
from pydantic import BaseModel, Field, field_validator
from app.validators import sanitize_string, sanitize_optional_string

class StudyItemBase(BaseModel):

    study_order_id: int = Field(..., gt=0, description="ID de la orden de estudio")
    study_type: str = Field(..., min_length=1, max_length=100, description="Tipo de estudio")
    assigned_doctor: str = Field(..., min_length=1, max_length=255, description="Doctor asignado al estudio")
    name: str = Field(..., min_length=1, max_length=200, description="Nombre del estudio")
    reason: str = Field(..., min_length=1, max_length=500, description="Motivo del estudio")
    document_date: date | None = Field(None, description="Fecha del documento")
    status: str = Field("pending", max_length=50, description="Estado del estudio")
    url: str | None = Field(None, max_length=500, description="URL del documento")

    @field_validator('study_type', 'name', 'reason', 'status')
    @classmethod
    def sanitize_required_strings(cls, v: str) -> str:
        """Sanitiza campos obligatorios"""
        sanitized = sanitize_string(v)
        if not sanitized:
            raise ValueError("Este campo no puede estar vacío")
        return sanitized
    
    @field_validator('assigned_doctor')
    @classmethod
    def sanitize_assigned_doctor(cls, v: str) -> str:
        sanitized = sanitize_string(v)
        if not sanitized:
            raise ValueError("Este campo no puede estar vacío")
        return sanitized

    @field_validator('url')
    @classmethod
    def sanitize_url(cls, v: str | None) -> str | None:
        """Sanitiza URL opcional"""
        return sanitize_optional_string(v)
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Valida que el estado sea válido"""
        valid_statuses = ['pending', 'completed', 'approved']
        v_lower = v.lower()
        if v_lower not in valid_statuses:
            raise ValueError(f"El estado debe ser uno de: {', '.join(valid_statuses)}")
        return v_lower


class StudyItemCreate(StudyItemBase):
    pass

class StudyItemUpdate(BaseModel):
    study_order_id: int | None = Field(None, gt=0, description="ID de la orden de estudio")
    study_type: str | None = Field(None, min_length=1, max_length=100, description="Tipo de estudio")
    name: str | None = Field(None, min_length=1, max_length=200, description="Nombre del estudio")
    reason: str | None = Field(None, min_length=1, max_length=500, description="Motivo del estudio")
    document_date: date | None = Field(None, description="Fecha del documento")
    status: str | None = Field(None, max_length=50, description="Estado del estudio")
    url: str | None = Field(None, max_length=500, description="URL del documento")
    assigned_doctor: str | None = Field(None, max_length=255, description="Doctor asignado al estudio")

    @field_validator('study_type', 'name', 'reason')
    @classmethod
    def sanitize_optional_strings(cls, v: str | None) -> str | None:
        """Sanitiza campos opcionales"""
        if v is None:
            return None
        sanitized = sanitize_string(v)
        if not sanitized:
            raise ValueError("Este campo no puede estar vacío")
        return sanitized

    @field_validator('assigned_doctor')
    @classmethod
    def sanitize_assigned_doctor(cls, v: str | None) -> str | None:
        """Sanitiza assigned_doctor (puede estar vacío)"""
        if v is None:
            return None
        return sanitize_string(v) if v else ""

    @field_validator('url')
    @classmethod
    def sanitize_url(cls, v: str | None) -> str | None:
        """Sanitiza URL opcional"""
        return sanitize_optional_string(v)

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        """Valida que el estado sea válido"""
        if v is None:
            return None
        valid_statuses = ['pending', 'completed', 'approved']
        v_lower = v.lower()
        if v_lower not in valid_statuses:
            raise ValueError(f"El estado debe ser uno de: {', '.join(valid_statuses)}")
        return v_lower

class StudyItemOut(StudyItemBase):
    id: int
    class Config:
        from_attributes = True
