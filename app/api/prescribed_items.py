from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.schemas.prescribed_item import PrescribedItemCreate, PrescribedItemUpdate, PrescribedItemOut
from app.services import prescribed_item_service

router = APIRouter(prefix="/prescribed-items", tags=["prescribed-items"])


@router.post("/", response_model=PrescribedItemOut, status_code=status.HTTP_201_CREATED)
def create(
    payload: PrescribedItemCreate, 
    db: Session = Depends(get_db),
    clear_existing: bool = False
):
    """
    Crea un prescribed_item.
    Si clear_existing es True, elimina todos los items existentes de la prescripción primero.
    Por defecto es False. Para reemplazar todos los items, usa el endpoint /prescription/{id}/replace
    """
    return prescribed_item_service.create_prescribed_item(db, payload, clear_existing=clear_existing)


@router.get("/", response_model=List[PrescribedItemOut])
def all(
    prescription_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return prescribed_item_service.list_prescribed_items(
        db,
        prescription_id=prescription_id,
        patient_id=patient_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{item_id}", response_model=PrescribedItemOut)
def get_one(item_id: int, db: Session = Depends(get_db)):
    obj = prescribed_item_service.get_prescribed_item(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Prescribed item not found")
    return obj


@router.put("/{item_id}", response_model=PrescribedItemOut)
def update(item_id: int, payload: PrescribedItemUpdate, db: Session = Depends(get_db)):
    obj = prescribed_item_service.update_prescribed_item(db, item_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Prescribed item not found")
    return obj


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(item_id: int, db: Session = Depends(get_db)):
    deleted = prescribed_item_service.delete_prescribed_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Prescribed item not found")


@router.post("/prescription/{prescription_id}/replace", response_model=List[PrescribedItemOut], status_code=status.HTTP_200_OK)
def replace_all(
    prescription_id: int,
    items: List[PrescribedItemCreate],
    db: Session = Depends(get_db),
):
    """
    Reemplaza todos los prescribed_items de una prescripción.
    Elimina los existentes y crea los nuevos para evitar duplicados.
    """
    # Verificar que la prescripción existe
    from app.models.prescription import Prescription
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    try:
        replaced_items = prescribed_item_service.replace_prescribed_items(db, prescription_id, items)
        return replaced_items
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al reemplazar items: {str(e)}"
        )
