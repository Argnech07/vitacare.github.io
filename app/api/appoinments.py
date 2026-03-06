# app/api/appointments.py
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db

from app.schemas.appoinments import AppointmentCreate, AppointmentOut, AppointmentUpdate
from app.services import appoinments_service as appointment_service

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
)


@router.post(
    "/",
    response_model=AppointmentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
):
    if appointment_service.exists_slot(
        db,
        visit_date=payload.visit_date,
        start_time=payload.start_time,
        doctor_id=payload.doctor_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cita en ese horario para este doctor",
        )

    try:
        obj = appointment_service.create(db, payload)
        return obj
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear la cita (verifica paciente/doctor y datos requeridos)",
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al crear la cita: {exc}",
        )


@router.get("/", response_model=List[AppointmentOut])
def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    items = appointment_service.list_appointments(
        db,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )
    return items


@router.get("/count")
def count_appointments(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    count = appointment_service.count_appointments(
        db,
        start_date=start_date,
        end_date=end_date,
    )
    return {"count": count}


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
):
    obj = appointment_service.get(db, appointment_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    return obj


@router.put("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(
    appointment_id: int,
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
):
    obj = appointment_service.get(db, appointment_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    # reutilizamos update, pero con todos los campos
    update_payload = AppointmentUpdate(**payload.dict())
    obj = appointment_service.update(db, appointment_id, update_payload)
    return obj


@router.patch("/{appointment_id}", response_model=AppointmentOut)
def partial_update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
):
    obj = appointment_service.update(db, appointment_id, payload)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    return obj


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
):
    ok = appointment_service.delete(db, appointment_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    return
