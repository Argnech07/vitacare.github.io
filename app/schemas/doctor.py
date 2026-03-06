from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.validators import (
    sanitize_string, 
    sanitize_optional_string, 
    validate_password_strength,
    validate_email_format
)

class DoctorBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="Nombre del doctor")
    last_name: str = Field(..., min_length=1, max_length=100, description="Apellido del doctor")
    middle_name: str | None = Field(None, max_length=100, description="Segundo nombre (opcional)")
    email: EmailStr = Field(..., max_length=255, description="Correo electrónico")
    license_number: str = Field(..., min_length=1, max_length=50, description="Número de licencia médica")
    license_number_E: str = Field(..., min_length=1, max_length=50, description="Número de cédula estatal")
    specialty: str = Field(..., min_length=1, max_length=100, description="Especialidad médica")

    @field_validator('first_name', 'last_name', 'license_number', 'license_number_E', 'specialty')
    @classmethod
    def sanitize_required_strings(cls, v: str) -> str:
        """Sanitiza campos obligatorios de tipo string"""
        sanitized = sanitize_string(v)
        if not sanitized:
            raise ValueError("Este campo no puede estar vacío")
        return sanitized

    @field_validator('middle_name')
    @classmethod
    def sanitize_middle_name(cls, v: str | None) -> str | None:
        """Sanitiza el campo middle_name opcional"""
        return sanitize_optional_string(v)

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Valida y sanitiza el email"""
        validated = validate_email_format(v)
        return validated or v  # Si es None, deja que EmailStr lo valide

class DoctorCreate(DoctorBase):
    password: str = Field(..., min_length=8, max_length=128, description="Contraseña (mínimo 8 caracteres)")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Valida que la contraseña tenga al menos 8 caracteres"""
        return validate_password_strength(v)

class DoctorOut(DoctorBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class DoctorUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    middle_name: str | None = Field(None, max_length=100)
    specialty: str | None = Field(None, min_length=1, max_length=100)
    license_number_E: str | None = Field(None, min_length=1, max_length=50)
    is_active: bool | None = None
    password: str | None = Field(None, min_length=8, max_length=128, description="Contraseña nueva (mínimo 8 caracteres)")

    @field_validator('first_name', 'last_name', 'specialty', 'license_number_E')
    @classmethod
    def sanitize_optional_strings(cls, v: str | None) -> str | None:
        """Sanitiza campos opcionales pero si están presentes deben tener valor"""
        if v is None:
            return None
        sanitized = sanitize_string(v)
        return sanitized if sanitized else None

    @field_validator('middle_name')
    @classmethod
    def sanitize_middle_name(cls, v: str | None) -> str | None:
        """Sanitiza el campo middle_name opcional"""
        return sanitize_optional_string(v)

    @field_validator('password')
    @classmethod
    def validate_password_update(cls, v: str | None) -> str | None:
        """Valida que la contraseña tenga al menos 8 caracteres si se proporciona"""
        if v is None:
            return None
        return validate_password_strength(v)
