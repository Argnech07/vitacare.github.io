from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.schemas.study_order import StudyOrderCreate, StudyOrderOut, StudyOrderFull
from app.schemas.study_item import StudyItemOut
from app.services import study_service
from app.services.security import get_current_admin
from app.models.admin import Admin

router = APIRouter(prefix="/study-orders", tags=["study-orders"])

@router.post("/", response_model=StudyOrderOut, status_code=status.HTTP_201_CREATED)
def create(payload: StudyOrderCreate, db: Session = Depends(get_db)):
    return study_service.create_study_order(db, payload)

@router.get("/", response_model=List[StudyOrderOut])
def all(
    patient_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    if patient_id:
        return study_service.list_study_orders_by_patient(db, patient_id, skip=skip, limit=limit)
    return study_service.list_study_orders(db, skip=skip, limit=limit)

@router.get("/pending", response_model=List[StudyOrderFull])
def get_pending_study_orders(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Obtiene todas las órdenes de estudio que tienen items pendientes de aprobación.
    Requiere autenticación de administrador.
    """
    orders = study_service.list_pending_study_orders(db, skip=skip, limit=limit)
    return orders

@router.get("/{order_id}", response_model=StudyOrderOut)
def get_one(order_id: int, db: Session = Depends(get_db)):
    order = study_service.get_study_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="StudyOrder not found")
    return order

@router.get("/{order_id}/full", response_model=StudyOrderFull)
def get_study_order_full(order_id: int, db: Session = Depends(get_db)):
    try:
        order = study_service.get_study_order_full(db, order_id)
    except Exception as e:
        # log temporal
        print(f"Error en get_study_order_full({order_id}): {e!r}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener la orden completa"
        )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de estudio no encontrada"
        )
    return order

@router.post("/{order_id}/approve", response_model=StudyOrderOut)
def approve_study_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Aprueba una orden de estudio cambiando el estado de todos sus items a 'approved'.
    
    Requiere autenticación de administrador.
    """
    order = study_service.approve_study_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de estudio no encontrada"
        )
    return order

@router.post("/{order_id}/reject", response_model=StudyOrderOut)
def reject_study_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Rechaza una orden de estudio cambiando el estado de todos sus items a 'cancelled'.
    
    Requiere autenticación de administrador.
    """
    try:
        order = study_service.get_study_order_full(db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orden de estudio no encontrada"
            )
        return order
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la orden de estudio: {str(e)}"
        )
