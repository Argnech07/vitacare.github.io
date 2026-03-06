from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.schemas.doctor import DoctorCreate, DoctorOut, DoctorUpdate
from app.services import doctor_service
from app.services.security import get_current_doctor, get_current_admin
from app.models.doctor import Doctor
from app.models.admin import Admin

router = APIRouter(prefix="/doctors", tags=["doctors"])

@router.post("/register", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
def register(
    payload: DoctorCreate,
    db: Session = Depends(get_db),
):
    """Registro público de doctor.

    Este endpoint existe para permitir que el formulario de registro cree un doctor
    sin requerir autenticación previa. Las rutas administrativas (/doctors/) siguen
    protegidas por get_current_admin.
    """
    try:
        return doctor_service.create_doctor(db, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al registrar el doctor: {str(e)}",
        )

@router.post("/", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
def create(
    payload: DoctorCreate, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Crea un nuevo doctor en el sistema.
    
    Requiere autenticación de administrador.
    
    Valida que:
    - El email no esté ya registrado
    - La cédula profesional no esté ya registrada
    - Todos los campos requeridos estén presentes y válidos
    """
    try:
        return doctor_service.create_doctor(db, payload)
    except HTTPException:
        # Re-lanzar HTTPException directamente (ya tiene el status y detail correctos)
        raise
    except Exception as e:
        # Capturar cualquier otro error inesperado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al crear el doctor: {str(e)}"
        )


@router.get("/me", response_model=DoctorOut)  
def read_me(current_doctor: Doctor = Depends(get_current_doctor)):
    return current_doctor


@router.get("/", response_model=List[DoctorOut])
def all(
    skip: int = 0, 
    limit: int = 50, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Lista todos los doctores. Requiere autenticación de administrador."""
    return doctor_service.list_doctors(db, skip=skip, limit=limit)


@router.get("/{doctor_id}", response_model=DoctorOut)
def get_one(
    doctor_id: int, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Obtiene un doctor por ID. Requiere autenticación de administrador."""
    doctor = doctor_service.get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return doctor
@router.put("/{doctor_id}", response_model=DoctorOut)
def modify(
    doctor_id: int, 
    payload: DoctorUpdate, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Actualiza un doctor. Requiere autenticación de administrador."""
    doc = doctor_service.update_doctor(db, doctor_id, payload)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return doc

@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(
    doctor_id: int, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Elimina un doctor. Requiere autenticación de administrador."""
    deleted = doctor_service.delete_doctor(db, doctor_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
