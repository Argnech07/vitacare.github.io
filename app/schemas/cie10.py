from pydantic import BaseModel, Field, field_validator
from app.validators import sanitize_string, sanitize_optional_string

class CIE10Base(BaseModel):
    code: str = Field(..., min_length=1, max_length=20, description="Código CIE-10")
    description: str = Field(..., min_length=1, max_length=500, description="Descripción del código")
    cie_group: str | None = Field(None, max_length=100, description="Grupo CIE-10")
    notes: str | None = Field(None, max_length=1000, description="Notas adicionales")

    @field_validator('code', 'description')
    @classmethod
    def sanitize_required_strings(cls, v: str) -> str:
        """Sanitiza campos obligatorios"""
        sanitized = sanitize_string(v)
        if not sanitized:
            raise ValueError("Este campo no puede estar vacío")
        return sanitized

    @field_validator('cie_group', 'notes')
    @classmethod
    def sanitize_optional_strings(cls, v: str | None) -> str | None:
        """Sanitiza campos opcionales"""
        return sanitize_optional_string(v)

class CIE10Create(CIE10Base):
    pass

class CIE10Out(CIE10Base):
    pass
