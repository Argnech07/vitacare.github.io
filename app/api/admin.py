from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.schemas.admin import AdminCreate, AdminOut, AdminUpdate
from app.services import admin_service
from app.services.security import get_current_admin
from app.models.admin import Admin

router = APIRouter(prefix="/admins", tags=["admins"])

@router.post("/", response_model=AdminOut, status_code=status.HTTP_201_CREATED)
def create(
    payload: AdminCreate, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Crea un nuevo administrador en el sistema.
    
    Requiere autenticación de administrador.
    
    Valida que:
    - El email no esté ya registrado
    - Todos los campos requeridos estén presentes y válidos
    """
    try:
        return admin_service.create_admin(db, payload)
    except HTTPException:
        # Re-lanzar HTTPException directamente (ya tiene el status y detail correctos)
        raise
    except Exception as e:
        # Capturar cualquier otro error inesperado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al crear el administrador: {str(e)}"
        )


@router.get("/me", response_model=AdminOut)  
def read_me(current_admin: Admin = Depends(get_current_admin)):
    """Obtiene la información del administrador autenticado"""
    return current_admin


@router.get("/", response_model=List[AdminOut])
def all(
    skip: int = 0, 
    limit: int = 50, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Lista todos los administradores. Requiere autenticación de administrador."""
    return admin_service.list_admins(db, skip=skip, limit=limit)


@router.get("/{admin_id}", response_model=AdminOut)
def get_one(
    admin_id: int, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Obtiene un administrador por ID. Requiere autenticación de administrador."""
    admin = admin_service.get_admin(db, admin_id)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrador no encontrado")
    return admin


@router.put("/{admin_id}", response_model=AdminOut)
def modify(
    admin_id: int, 
    payload: AdminUpdate, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Actualiza un administrador. Requiere autenticación de administrador."""
    admin = admin_service.update_admin(db, admin_id, payload)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrador no encontrado")
    return admin


@router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(
    admin_id: int, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Elimina un administrador. Requiere autenticación de administrador."""
    deleted = admin_service.delete_admin(db, admin_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrador no encontrado")

