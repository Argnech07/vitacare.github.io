from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from pydantic import ValidationError
import logging
from datetime import datetime

from app.models.patient import Patient
from app.models.vitals import Vitals
from app.schemas.patient import PatientCreate, PatientUpdate, PatientOut, PatientListItem

logger = logging.getLogger(__name__)

def _patient_to_out_safe(pat: Patient) -> Optional[PatientOut]:
    try:
        return PatientOut.model_validate(pat)
    except ValidationError as e:
        logger.warning(f"Error de validación para paciente ID {getattr(pat, 'id', 'N/A')}: {e.errors()}")
        try:
            first_name = (pat.first_name or '').strip()
            last_name = (pat.last_name or '').strip()

            patient_dict = {
                "id": pat.id,
                "first_name": first_name if first_name else "N/A",
                "last_name": last_name if last_name else "N/A",
                "middle_name": (pat.middle_name or None),
                "curp": None if pat.curp and len(pat.curp) != 18 else (pat.curp or None),
                "birth_date": pat.birth_date,
                "gender": (pat.gender or None),
                "phone": (pat.phone or None),
                "email": (pat.email or None),
                "city": (pat.city or None),
                "street": (pat.street or None),
                "postal_code": None
                if pat.postal_code and len(pat.postal_code) != 5
                else (pat.postal_code or None),
                "marital_status": (pat.marital_status or None),
                "education": (pat.education or None),
                "occupation": (pat.occupation or None),
                "origin": (pat.origin or None),
                "worker_type": (getattr(pat, 'worker_type', None) or None),
                "blood_type": (pat.blood_type or None),
                "profile_picture": (pat.profile_picture or None),
                "is_active": bool(pat.is_active),
                "created_at": pat.created_at,
            }

            try:
                return PatientOut.model_validate(patient_dict)
            except ValidationError:
                patient_dict["email"] = None
                patient_dict["phone"] = None
                patient_dict["postal_code"] = None
                patient_dict["curp"] = None
                patient_dict["middle_name"] = None
                patient_dict["city"] = None
                patient_dict["street"] = None
                patient_dict["marital_status"] = None
                patient_dict["education"] = None
                patient_dict["gender"] = None
                patient_dict["blood_type"] = None
                patient_dict["profile_picture"] = None
                return PatientOut.model_validate(patient_dict)
        except Exception as e2:
            logger.error(f"No se pudo serializar paciente ID {getattr(pat, 'id', 'N/A')}: {e2}")
            return None

def create_patient(db: Session, payload: PatientCreate) -> PatientOut:
    # Validar CURP única
    if payload.curp:
        existing = db.query(Patient).filter(Patient.curp == payload.curp).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A patient with this CURP already exists",
            )

    pat = Patient(
        first_name=payload.first_name,
        last_name=payload.last_name,
        middle_name=payload.middle_name,
        curp=payload.curp,
        birth_date=payload.birth_date,
        gender=payload.gender,
        phone=payload.phone,
        email=payload.email,
        city=payload.city,
        street=payload.street,
        postal_code=payload.postal_code,
        marital_status=payload.marital_status,
        education=payload.education,
        occupation=payload.occupation,
        origin=payload.origin,
        worker_type=payload.worker_type,
        blood_type=payload.blood_type,
        profile_picture=payload.profile_picture,
        is_active=payload.is_active,
    )
    db.add(pat)
    db.commit()
    db.refresh(pat)

    # Crear registro de signos vitales por defecto (N/A -> null) con fecha/hora actual
    try:
        default_vitals = Vitals(
            patient_id=pat.id,
            taken_at=datetime.utcnow(),
        )
        db.add(default_vitals)
        db.commit()
    except Exception as e:
        logging.getLogger(__name__).warning(
            f"No se pudo crear vitals por defecto para paciente {pat.id}: {e}"
        )

    return PatientOut.model_validate(pat)

def get_patient(db: Session, patient_id: int) -> Optional[PatientOut]:
    pat = db.query(Patient).filter(Patient.id == patient_id).first()
    if not pat:
        return None
    return _patient_to_out_safe(pat)

def update_patient(
    db: Session, patient_id: int, payload: PatientUpdate
) -> Optional[PatientOut]:
    pat = db.query(Patient).filter(Patient.id == patient_id).first()
    if not pat:
        return None

    # Validar CURP única en update
    if payload.curp:
        existing = db.query(Patient).filter(Patient.curp == payload.curp).first()
        if existing is not None and existing.id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A patient with this CURP already exists",
            )

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(pat, field, value)

    db.commit()
    db.refresh(pat)
    return _patient_to_out_safe(pat)

def delete_patient(db: Session, patient_id: int) -> bool:
    pat = db.query(Patient).filter(Patient.id == patient_id).first()
    if not pat:
        return False
    db.delete(pat)
    db.commit()
    return True

def list_patients(
    db: Session, skip: int = 0, limit: int = 50, search: Optional[str] = None, is_active: Optional[bool] = None
) -> List[PatientOut]:
    query = db.query(Patient)

    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                Patient.first_name.ilike(term),
                Patient.last_name.ilike(term),
                Patient.middle_name.ilike(term),
                Patient.email.ilike(term),
                Patient.curp.ilike(term),
            )
        )
    
    if is_active is not None:
        query = query.filter(Patient.is_active == is_active)

    patients = (
        query.order_by(Patient.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    result: List[PatientOut] = []
    for p in patients:
        out = _patient_to_out_safe(p)
        if out is not None:
            result.append(out)
    return result

def get_patients_count(db: Session, search: Optional[str] = None, is_active: Optional[bool] = None) -> int:
    query = db.query(Patient)
    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                Patient.first_name.ilike(term),
                Patient.last_name.ilike(term),
                Patient.middle_name.ilike(term),
                Patient.email.ilike(term),
                Patient.curp.ilike(term),
            )
        )
    if is_active is not None:
        query = query.filter(Patient.is_active == is_active)
    return query.count()

def list_patients_basic(
    db: Session, skip: int = 0, limit: int = 1000, search: Optional[str] = None, is_active: Optional[bool] = None
) -> List[PatientListItem]:
    """
    Lista pacientes con solo id y full_name. Optimizado para listas grandes.
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a saltar
        limit: Número máximo de registros a devolver (hasta 1000)
        search: Término de búsqueda opcional
        is_active: Filtro por estado activo opcional
    
    Returns:
        Lista de PatientListItem con id y full_name
    """
    query = db.query(Patient)

    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                Patient.first_name.ilike(term),
                Patient.last_name.ilike(term),
                Patient.middle_name.ilike(term),
            )
        )
    
    if is_active is not None:
        query = query.filter(Patient.is_active == is_active)

    patients = (
        query.order_by(Patient.last_name, Patient.first_name)
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for p in patients:
        # Construir full_name: first_name + (middle_name si existe) + last_name
        name_parts = [p.first_name]
        if p.middle_name:
            name_parts.append(p.middle_name)
        name_parts.append(p.last_name)
        full_name = " ".join(name_parts)
        
        result.append(PatientListItem(
            id=p.id,
            full_name=full_name
        ))
    
    return result

def toggle_patient_active(db: Session, patient_id: int) -> Optional[PatientOut]:
    """
    Invierte el estado is_active de un paciente.
    
    Args:
        db: Sesión de base de datos
        patient_id: ID del paciente a modificar
    
    Returns:
        PatientOut si el paciente existe, None si no existe
    """
    pat = db.query(Patient).filter(Patient.id == patient_id).first()
    if not pat:
        return None
    
    # Invertir el estado de is_active
    pat.is_active = not pat.is_active
    
    db.commit()
    db.refresh(pat)
    
    try:
        return PatientOut.model_validate(pat)
    except ValidationError as e:
        # Manejar errores de validación para datos existentes
        logger.warning(f"Error de validación para paciente ID {patient_id}: {e.errors()}")
        try:
            patient_dict = {
                "id": pat.id,
                "first_name": pat.first_name,
                "last_name": pat.last_name,
                "middle_name": pat.middle_name,
                "curp": None if pat.curp and len(pat.curp) != 18 else pat.curp,
                "birth_date": pat.birth_date,
                "gender": pat.gender,
                "phone": pat.phone,
                "email": pat.email,
                "city": pat.city,
                "street": pat.street,
                "postal_code": None if pat.postal_code and len(pat.postal_code) != 5 else pat.postal_code,
                "marital_status": pat.marital_status,
                "education": pat.education,
                "blood_type": pat.blood_type,
                "profile_picture": pat.profile_picture,
                "is_active": pat.is_active,
                "created_at": pat.created_at,
            }
            return PatientOut.model_validate(patient_dict)
        except Exception as e2:
            logger.error(f"No se pudo serializar paciente ID {patient_id}: {e2}")
            return None
