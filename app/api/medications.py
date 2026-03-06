from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.schemas.medication import MedicationCreate, MedicationUpdate, MedicationOut
from app.services import medication_service

router = APIRouter(prefix="/medications", tags=["medications"])

@router.post("/", response_model=MedicationOut, status_code=status.HTTP_201_CREATED)
def create(payload: MedicationCreate, db: Session = Depends(get_db)):
    return medication_service.create_medication(db, payload)

@router.get("/", response_model=List[MedicationOut])
def all(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return medication_service.list_medications(db, skip=skip, limit=limit)

@router.get("/{medication_id}", response_model=MedicationOut)
def get_one(medication_id: int, db: Session = Depends(get_db)):
    obj = medication_service.get_medication(db, medication_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Medication not found")
    return obj

@router.put("/{medication_id}", response_model=MedicationOut)
def update(medication_id: int, payload: MedicationUpdate, db: Session = Depends(get_db)):
    obj = medication_service.update_medication(db, medication_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Medication not found")
    return obj

@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(medication_id: int, db: Session = Depends(get_db)):
    deleted = medication_service.delete_medication(db, medication_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Medication not found")
