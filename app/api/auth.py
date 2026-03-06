from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.doctor import Doctor
from app.models.admin import Admin
from app.schemas.auth import Token
from app.services.security import create_access_token
from app.services.passwords import verify_password
from app.validators import sanitize_string, validate_email_format


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # Sanitizar y validar email (username)
    if not form_data.username or not form_data.username.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email es requerido",
        )
    
    email = sanitize_string(form_data.username).lower()
    
    # Validar formato de email
    try:
        email = validate_email_format(email) or email
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El formato del email no es válido",
        )
    
    # Validar que la contraseña no esté vacía
    if not form_data.password or not form_data.password.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña es requerida",
        )
    
    # Validar longitud máxima de contraseña (bcrypt limita a 72 bytes)
    password_bytes = form_data.password.encode('utf-8')
    if len(password_bytes) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña es demasiado larga (máximo 72 bytes)",
        )
    
    # Buscar doctor por email
    doctor = db.query(Doctor).filter(Doctor.email == email).first()
    
    # Validar credenciales (no distinguir entre usuario no encontrado y contraseña incorrecta por seguridad)
    if not doctor or not verify_password(form_data.password, doctor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    
    # Verificar que el doctor esté activo
    if not doctor.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere acceso por el administrador",
        )

    # sub como string (requisito de jose)
    access_token = create_access_token({"sub": str(doctor.id), "type": "doctor"})

    return Token(access_token=access_token, token_type="bearer")


@router.post("/admin/login", response_model=Token)
def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login para administradores.
    
    Busca admin por email, valida contraseña, verifica que esté activo
    y genera token JWT con tipo "admin" en el payload.
    """
    # Sanitizar y validar email (username)
    if not form_data.username or not form_data.username.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email es requerido",
        )
    
    email = sanitize_string(form_data.username).lower()
    
    # Validar formato de email
    try:
        email = validate_email_format(email) or email
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El formato del email no es válido",
        )
    
    # Validar que la contraseña no esté vacía
    if not form_data.password or not form_data.password.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña es requerida",
        )
    
    # Validar longitud máxima de contraseña (bcrypt limita a 72 bytes)
    password_bytes = form_data.password.encode('utf-8')
    if len(password_bytes) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña es demasiado larga (máximo 72 bytes)",
        )
    
    # Buscar admin por email
    admin = db.query(Admin).filter(Admin.email == email).first()
    
    # Validar credenciales (no distinguir entre usuario no encontrado y contraseña incorrecta por seguridad)
    if not admin or not verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    
    # Verificar que el admin esté activo
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta de administrador desactivada",
        )

    # sub como string (requisito de jose) con tipo "admin"
    access_token = create_access_token({"sub": str(admin.id), "type": "admin"})

    return Token(access_token=access_token, token_type="bearer")
