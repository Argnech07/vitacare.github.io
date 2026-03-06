"""
Módulo de validación y sanitización para VitaCare Backend
Proporciona funciones para sanitizar entradas y validar datos
"""
import re
from typing import Any, Optional
from pydantic import field_validator, Field
from pydantic_core import core_schema


def sanitize_string(value: str) -> str:
    """
    Sanitiza un string removiendo espacios en blanco al inicio y final,
    y normalizando espacios múltiples a uno solo.
    
    Args:
        value: String a sanitizar
        
    Returns:
        String sanitizado o cadena vacía si el valor es None
    """
    if value is None:
        return ""
    if not isinstance(value, str):
        return str(value).strip()
    return " ".join(value.strip().split())


def sanitize_optional_string(value: Optional[str]) -> Optional[str]:
    """
    Sanitiza un string opcional.
    
    Args:
        value: String opcional a sanitizar
        
    Returns:
        String sanitizado o None si está vacío
    """
    if value is None:
        return None
    sanitized = sanitize_string(value)
    return sanitized if sanitized else None


def validate_password_strength(password: str) -> str:
    """
    Valida que la contraseña tenga al menos 8 caracteres.
    
    Args:
        password: Contraseña a validar
        
    Returns:
        Contraseña validada
        
    Raises:
        ValueError: Si la contraseña no cumple con los requisitos
    """
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    return password


def validate_curp_format(curp: Optional[str]) -> Optional[str]:
    """
    Valida el formato básico de CURP (18 caracteres alfanuméricos).
    
    Args:
        curp: CURP a validar
        
    Returns:
        CURP en mayúsculas y sanitizado o None
        
    Raises:
        ValueError: Si el formato no es válido
    """
    if curp is None:
        return None
    curp = sanitize_string(curp).upper()
    if not curp:
        return None
    # Validar longitud: debe tener 18 caracteres
    if len(curp) != 18:
        raise ValueError("El CURP debe tener exactamente 18 caracteres")
    # Validar formato básico: 4 letras, 6 dígitos, 1 letra (H/M), 5 letras, 1 alfanumérico, 1 dígito
    if not re.match(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[0-9A-Z]\d$', curp):
        raise ValueError("El formato del CURP no es válido")
    return curp


def validate_phone(phone: Optional[str]) -> Optional[str]:
    """
    Valida y sanitiza un número de teléfono.
    
    Args:
        phone: Número de teléfono a validar
        
    Returns:
        Teléfono sanitizado (solo dígitos) o None
    """
    if phone is None:
        return None
    # Remover espacios, guiones, paréntesis, etc.
    cleaned = re.sub(r'[^\d+]', '', phone)
    if not cleaned:
        return None
    # Validar longitud mínima (al menos 10 dígitos para números mexicanos)
    if len(cleaned.replace('+', '')) < 10:
        raise ValueError("El número de teléfono debe tener al menos 10 dígitos")
    return cleaned


def validate_postal_code(postal_code: Optional[str]) -> Optional[str]:
    """
    Valida el código postal mexicano (5 dígitos).
    
    Args:
        postal_code: Código postal a validar
        
    Returns:
        Código postal validado o None
    """
    if postal_code is None:
        return None
    cleaned = sanitize_string(postal_code)
    if not cleaned:
        return None
    # Validar formato: 5 dígitos
    if not re.match(r'^\d{5}$', cleaned):
        raise ValueError("El código postal debe tener 5 dígitos")
    return cleaned


def validate_email_format(email: Optional[str]) -> Optional[str]:
    """
    Valida y sanitiza un email.
    
    Args:
        email: Email a validar
        
    Returns:
        Email en minúsculas y sanitizado o None
    """
    if email is None:
        return None
    email = sanitize_string(email).lower()
    if not email:
        return None
    # Validación básica de formato
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("El formato del email no es válido")
    return email


def validate_required_field(value: Any, field_name: str) -> Any:
    """
    Valida que un campo obligatorio no esté vacío.
    
    Args:
        value: Valor a validar
        field_name: Nombre del campo para mensaje de error
        
    Returns:
        Valor validado
        
    Raises:
        ValueError: Si el campo está vacío o es None
    """
    if value is None:
        raise ValueError(f"El campo '{field_name}' es obligatorio")
    if isinstance(value, str) and not sanitize_string(value):
        raise ValueError(f"El campo '{field_name}' no puede estar vacío")
    return value

