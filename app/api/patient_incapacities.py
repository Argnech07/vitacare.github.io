from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.patient_incapacity import (
    PatientIncapacityCreate,
    PatientIncapacityOut,
    PatientIncapacityUpdate,
)
from app.services import patient_incapacity_service


router = APIRouter(
    prefix="/patients/{patient_id}/incapacities",
    tags=["patient_incapacities"],
)


@router.get("/", response_model=List[PatientIncapacityOut])
def list_patient_incapacities(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    items = patient_incapacity_service.list_by_patient(
        db, patient_id=patient_id, skip=skip, limit=limit
    )
    return [PatientIncapacityOut.model_validate(x) for x in items]


@router.post(
    "/",
    response_model=PatientIncapacityOut,
    status_code=status.HTTP_201_CREATED,
)
def create_patient_incapacity(
    patient_id: int,
    payload: PatientIncapacityCreate,
    db: Session = Depends(get_db),
):
    obj = patient_incapacity_service.create_for_patient(db, patient_id, payload)
    return PatientIncapacityOut.model_validate(obj)


@router.patch(
    "/{incapacity_id}",
    response_model=PatientIncapacityOut,
)
def update_patient_incapacity(
    patient_id: int,
    incapacity_id: int,
    payload: PatientIncapacityUpdate,
    db: Session = Depends(get_db),
):
    obj = patient_incapacity_service.update_for_patient(
        db,
        patient_id=patient_id,
        incapacity_id=incapacity_id,
        payload=payload,
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Incapacity not found")
    return PatientIncapacityOut.model_validate(obj)


@router.delete(
    "/{incapacity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_patient_incapacity(
    patient_id: int,
    incapacity_id: int,
    db: Session = Depends(get_db),
):
    ok = patient_incapacity_service.delete_for_patient(
        db,
        patient_id=patient_id,
        incapacity_id=incapacity_id,
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Incapacity not found")
    return None
