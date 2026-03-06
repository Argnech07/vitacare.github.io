from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.vitals import VitalsCreate, VitalsOut, VitalsUpdate
from app.services import vitals_service


router = APIRouter(
    prefix="/patients/{patient_id}/vitals",
    tags=["vitals"],
)


@router.get("/latest", response_model=VitalsOut | None)
def get_latest_vitals(patient_id: int, db: Session = Depends(get_db)):
    vitals = vitals_service.get_latest_vitals(db, patient_id)
    if not vitals:
        return None
    
    return VitalsOut.model_validate(vitals)
    



@router.get("/", response_model=List[VitalsOut])
def list_vitals(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    vitals = vitals_service.list_vitals(db, patient_id, skip=skip, limit=limit)
    # v2:
    return [VitalsOut.model_validate(v) for v in vitals]
    # v1:
    # return [VitalsOut.from_orm(v) for v in vitals]


@router.post("/", response_model=VitalsOut, status_code=status.HTTP_201_CREATED)
def create_vitals(
    patient_id: int,
    payload: VitalsCreate,
    db: Session = Depends(get_db),
):
    vitals = vitals_service.create_vitals(db, patient_id, payload)
    return VitalsOut.model_validate(vitals)  # o from_orm


@router.put("/{vitals_id}", response_model=VitalsOut)
def update_vitals(
    patient_id: int,
    vitals_id: int,
    payload: VitalsUpdate,
    db: Session = Depends(get_db),
):
    vitals = vitals_service.update_vitals(db, vitals_id, payload)
    if not vitals or vitals.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vitals record not found for this patient",
        )
    return VitalsOut.model_validate(vitals)
