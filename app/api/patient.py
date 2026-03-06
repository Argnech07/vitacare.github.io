from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.patient import PatientCreate, PatientOut, PatientUpdate, PatientListItem
from app.services import patient_service
from app.services.security import get_current_admin
from app.models.admin import Admin

router = APIRouter(prefix="/patients", tags=["patients"])

@router.get("/", response_model=List[PatientOut])
def get_patients(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Records to return"),
    search: Optional[str] = Query(None, max_length=200, description="Search by name/email/CURP"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
):
    return patient_service.list_patients(db, skip=skip, limit=limit, search=search, is_active=is_active)

@router.get("/list", response_model=List[PatientListItem])
def get_patients_list(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(1000, ge=1, le=1000, description="Records to return (max 1000)"),
    search: Optional[str] = Query(None, max_length=200, description="Search by name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
):
    """
    Obtiene una lista simplificada de pacientes con solo id y full_name.
    Optimizado para listas grandes con límite de 1000 registros.
    """
    return patient_service.list_patients_basic(db, skip=skip, limit=limit, search=search, is_active=is_active)

@router.get("/count")
def get_patients_count(
    search: Optional[str] = Query(None, max_length=200, description="Same search filter as list"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
):
    count = patient_service.get_patients_count(db, search=search, is_active=is_active)
    return {"count": count}

@router.get("/{patient_id}", response_model=PatientOut)
def get_one(patient_id: int, db: Session = Depends(get_db)):
    pat = patient_service.get_patient(db, patient_id)
    if not pat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return pat

@router.post("/", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create(payload: PatientCreate, db: Session = Depends(get_db)):
    return patient_service.create_patient(db, payload)

@router.put("/{patient_id}", response_model=PatientOut)
def modify(patient_id: int, payload: PatientUpdate, db: Session = Depends(get_db)):
    pat = patient_service.update_patient(db, patient_id, payload)
    if not pat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return pat

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(patient_id: int, db: Session = Depends(get_db)):
    deleted = patient_service.delete_patient(db, patient_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

@router.patch("/{patient_id}/toggle-active", response_model=PatientOut)
def toggle_active(
    patient_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Activa o desactiva un paciente invirtiendo su estado is_active.
    
    Requiere autenticación de administrador.
    """
    patient = patient_service.toggle_patient_active(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    return patient
