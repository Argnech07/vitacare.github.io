from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate
from typing import List, Optional
from app.services.passwords import get_password_hash


def create_doctor(db: Session, data: DoctorCreate) -> Doctor:
    # Validar email único
    existing_email = db.query(Doctor).filter(Doctor.email == data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un doctor con este email",
        )
    
    # Validar cédula profesional única
    existing_license = db.query(Doctor).filter(Doctor.license_number == data.license_number).first()
    if existing_license:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un doctor con esta cédula profesional",
        )
    
    hashed = get_password_hash(data.password)
    obj = Doctor(
        first_name=data.first_name,
        last_name=data.last_name,
        middle_name=data.middle_name,
        email=data.email,
        license_number=data.license_number,
        license_number_E=data.license_number_E,
        specialty=data.specialty,
        hashed_password=hashed,
        is_active=False,
    )
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError as e:
        db.rollback()
        # Determinar qué campo causó el error
        error_detail = "Error al crear el doctor"
        error_str = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "email" in error_str.lower():
            error_detail = "Ya existe un doctor con este email"
        elif "license_number" in error_str.lower() or "cedula" in error_str.lower():
            error_detail = "Ya existe un doctor con esta cédula profesional"
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail,
        )

def list_doctors(db: Session, skip=0, limit=50) -> List[Doctor]:
    return db.query(Doctor).offset(skip).limit(limit).all()

def get_doctor(db: Session, doctor_id: int) -> Optional[Doctor]:
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()

def update_doctor(db: Session, doctor_id: int, data: DoctorUpdate) -> Optional[Doctor]:
    doc = get_doctor(db, doctor_id)
    if not doc:
        return None
    
    upd = data.model_dump(exclude_unset=True)
    
    # Validar email único si se está actualizando
    if "email" in upd:
        existing = db.query(Doctor).filter(Doctor.email == upd["email"]).first()
        if existing and existing.id != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro doctor con este email",
            )
    
    # Validar cédula profesional única si se está actualizando
    if "license_number" in upd:
        existing = db.query(Doctor).filter(Doctor.license_number == upd["license_number"]).first()
        if existing and existing.id != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro doctor con esta cédula profesional",
            )
    
    if upd.get("password"):
        # Usar get_password_hash en lugar de bcrypt.hash directamente
        doc.hashed_password = get_password_hash(upd.pop("password"))
    
    for k, v in upd.items():
        setattr(doc, k, v)
    
    try:
        db.commit()
        db.refresh(doc)
        return doc
    except IntegrityError as e:
        db.rollback()
        # Determinar qué campo causó el error
        error_detail = "Error al actualizar el doctor"
        error_str = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "email" in error_str.lower():
            error_detail = "Ya existe otro doctor con este email"
        elif "license_number" in error_str.lower() or "cedula" in error_str.lower():
            error_detail = "Ya existe otro doctor con esta cédula profesional"
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail,
        )

def delete_doctor(db: Session, doctor_id: int) -> bool:
    doc = get_doctor(db, doctor_id)
    if not doc:
        return False
    db.delete(doc)
    db.commit()
    return True
