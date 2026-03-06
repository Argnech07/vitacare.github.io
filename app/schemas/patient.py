from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.validators import (
    sanitize_string,
    sanitize_optional_string,
    validate_phone,
    validate_postal_code,
    validate_email_format
)

class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="Nombre del paciente")
    last_name: str = Field(..., min_length=1, max_length=100, description="Apellido del paciente")
    middle_name: str | None = Field(None, max_length=100, description="Segundo nombre (opcional)")
    curp: str | None = Field(None, max_length=18, description="CURP del paciente")
    birth_date: date | None = Field(None, description="Fecha de nacimiento")
    gender: str | None = Field(None, max_length=20, description="Género")
    phone: str | None = Field(None, max_length=20, description="Teléfono")
    email: EmailStr | None = Field(None, max_length=255, description="Correo electrónico")
    city: str | None = Field(None, max_length=100, description="Ciudad")
    street: str | None = Field(None, max_length=255, description="Calle y número")
    postal_code: str | None = Field(None, max_length=5, description="Código postal")
    marital_status: str | None = Field(None, max_length=50, description="Estado civil")
    education: str | None = Field(None, max_length=100, description="Nivel educativo")
    occupation: str | None = Field(None, max_length=100, description="Ocupación")
    origin: str | None = Field(None, max_length=100, description="Procedencia")
    worker_type: str | None = Field(None, max_length=20, description="Trabajador o dependiente")
    blood_type: str | None = Field(None, max_length=10, description="Tipo de sangre")
    profile_picture: str | None = Field(None, max_length=500, description="URL de foto de perfil")
    is_active: bool = Field(True, description="Estado activo del paciente")

    @field_validator('first_name', 'last_name')
    @classmethod
    def sanitize_required_strings(cls, v: str) -> str:
        """Sanitiza campos obligatorios"""
        sanitized = sanitize_string(v)
        if not sanitized:
            raise ValueError("Este campo no puede estar vacío")
        return sanitized

    @field_validator('middle_name', 'city', 'street', 'marital_status', 'education', 'occupation', 'origin', 'worker_type', 'gender', 'blood_type')
    @classmethod
    def sanitize_optional_strings(cls, v: str | None) -> str | None:
        """Sanitiza campos opcionales de tipo string"""
        return sanitize_optional_string(v)

    @field_validator('phone')
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        """Valida y sanitiza número de teléfono"""
        return validate_phone(v)

    @field_validator('email', mode='before')
    @classmethod
    def validate_email_field(cls, v: str | None):
        """Valida formato de email"""
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            return None
        validated = validate_email_format(v)
        return validated or v  # Si es None, deja que EmailStr lo valide

    @field_validator('postal_code')
    @classmethod
    def validate_postal_code_field(cls, v: str | None) -> str | None:
        """Valida código postal mexicano"""
        return validate_postal_code(v)

    @field_validator('profile_picture')
    @classmethod
    def sanitize_profile_picture(cls, v: str | None) -> str | None:
        """Sanitiza URL de foto de perfil"""
        return sanitize_optional_string(v)


class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    middle_name: str | None = Field(None, max_length=100)
    curp: str | None = Field(None, max_length=18)
    birth_date: date | None = None
    gender: str | None = Field(None, max_length=20)
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=100)
    street: str | None = Field(None, max_length=255)
    postal_code: str | None = Field(None, max_length=5)
    marital_status: str | None = Field(None, max_length=50)
    education: str | None = Field(None, max_length=100)
    occupation: str | None = Field(None, max_length=100)
    origin: str | None = Field(None, max_length=100)
    worker_type: str | None = Field(None, max_length=20)
    blood_type: str | None = Field(None, max_length=10)
    is_active: bool | None = None
    profile_picture: str | None = Field(None, max_length=500)

    @field_validator('first_name', 'last_name')
    @classmethod
    def sanitize_optional_required_strings(cls, v: str | None) -> str | None:
        """Sanitiza campos que si están presentes deben tener valor"""
        if v is None:
            return None
        sanitized = sanitize_string(v)
        return sanitized if sanitized else None

    @field_validator('middle_name', 'city', 'street', 'marital_status', 'education', 'occupation', 'origin', 'worker_type', 'gender', 'blood_type')
    @classmethod
    def sanitize_optional_strings(cls, v: str | None) -> str | None:
        """Sanitiza campos opcionales"""
        return sanitize_optional_string(v)

    @field_validator('phone')
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        """Valida y sanitiza número de teléfono"""
        return validate_phone(v)

    @field_validator('email', mode='before')
    @classmethod
    def validate_email_field(cls, v: str | None):
        """Valida formato de email"""
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            return None
        validated = validate_email_format(v)
        return validated or v

    @field_validator('postal_code')
    @classmethod
    def validate_postal_code_field(cls, v: str | None) -> str | None:
        """Valida código postal mexicano"""
        return validate_postal_code(v)

    @field_validator('profile_picture')
    @classmethod
    def sanitize_profile_picture(cls, v: str | None) -> str | None:
        """Sanitiza URL de foto de perfil"""
        return sanitize_optional_string(v)

class PatientOut(PatientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PatientListItem(BaseModel):
    """Schema simplificado para listas de pacientes con solo id y nombre completo"""
    id: int
    full_name: str = Field(..., description="Nombre completo del paciente")

    class Config:
        from_attributes = True
