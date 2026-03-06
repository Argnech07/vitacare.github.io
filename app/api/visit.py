from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.schemas.visit import VisitCreate, VisitFull, VisitOut, VisitUpdate
from app.services import visit_service

router = APIRouter(prefix="/visits", tags=["visits"])

@router.post("/", response_model=VisitOut, status_code=status.HTTP_201_CREATED)
def create(payload: VisitCreate, db: Session = Depends(get_db)):
    return visit_service.create_visit(db, payload)

@router.get("/", response_model=List[VisitOut])
def list_all(
    patient_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    return visit_service.list_visits(db, patient_id=patient_id, skip=skip, limit=limit)

@router.get("/{visit_id}", response_model=VisitOut)
def get_one(visit_id: int, db: Session = Depends(get_db)):
    visit = visit_service.get_visit(db, visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit

@router.put("/{visit_id}", response_model=VisitOut)
def modify(visit_id: int, payload: VisitUpdate, db: Session = Depends(get_db)):
    visit = visit_service.update_visit(db, visit_id, payload)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit

@router.delete("/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(visit_id: int, db: Session = Depends(get_db)):
    deleted = visit_service.delete_visit(db, visit_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Visit not found")

@router.get("/{visit_id}/full", response_model=VisitFull)
def get_visit_full(visit_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una visita completa con todos sus diagnósticos enriquecidos con CIE10
    """
    visit = visit_service.get_visit_full(db, visit_id)
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visita no encontrada"
        )
    return visit