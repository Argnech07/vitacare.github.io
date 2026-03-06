from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.admin import Admin
from app.schemas.admin import AdminCreate, AdminUpdate
from typing import List, Optional
from app.services.passwords import get_password_hash


def create_admin(db: Session, data: AdminCreate) -> Admin:
    # Validar email único
    existing_email = db.query(Admin).filter(Admin.email == data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un administrador con este email",
        )
    
    hashed = get_password_hash(data.password)
    obj = Admin(
        first_name=data.first_name,
        last_name=data.last_name,
        middle_name=data.middle_name,
        email=data.email,
        hashed_password=hashed,
    )
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError as e:
        db.rollback()
        # Determinar qué campo causó el error
        error_detail = "Error al crear el administrador"
        error_str = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "email" in error_str.lower():
            error_detail = "Ya existe un administrador con este email"
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail,
        )

def list_admins(db: Session, skip=0, limit=50) -> List[Admin]:
    return db.query(Admin).offset(skip).limit(limit).all()

def get_admin(db: Session, admin_id: int) -> Optional[Admin]:
    return db.query(Admin).filter(Admin.id == admin_id).first()

def update_admin(db: Session, admin_id: int, data: AdminUpdate) -> Optional[Admin]:
    admin = get_admin(db, admin_id)
    if not admin:
        return None
    
    upd = data.model_dump(exclude_unset=True)
    
    # Validar email único si se está actualizando
    if "email" in upd:
        existing = db.query(Admin).filter(Admin.email == upd["email"]).first()
        if existing and existing.id != admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro administrador con este email",
            )
    
    if upd.get("password"):
        # Usar get_password_hash en lugar de bcrypt.hash directamente
        admin.hashed_password = get_password_hash(upd.pop("password"))
    
    for k, v in upd.items():
        setattr(admin, k, v)
    
    try:
        db.commit()
        db.refresh(admin)
        return admin
    except IntegrityError as e:
        db.rollback()
        # Determinar qué campo causó el error
        error_detail = "Error al actualizar el administrador"
        error_str = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "email" in error_str.lower():
            error_detail = "Ya existe otro administrador con este email"
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail,
        )

def delete_admin(db: Session, admin_id: int) -> bool:
    admin = get_admin(db, admin_id)
    if not admin:
        return False
    db.delete(admin)
    db.commit()
    return True

