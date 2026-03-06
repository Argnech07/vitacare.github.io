# app/services/appointment_service.py
from datetime import datetime, timedelta, time
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.appoinments import Appointment
from app.schemas.appoinments import AppointmentCreate, AppointmentUpdate


def _add_30_minutes(start_time: time) -> time:
    dt = datetime.combine(datetime.today().date(), start_time)
    dt_end = dt + timedelta(minutes=30)
    return dt_end.time()


def exists_slot(
    db: Session,
    *,
    visit_date,
    start_time,
    doctor_id: int,
) -> bool:
    q = (
        db.query(Appointment)
        .filter(
            Appointment.visit_date == visit_date,
            Appointment.start_time == start_time,
            Appointment.doctor_id == doctor_id,
        )
    )
    return db.query(q.exists()).scalar()


def create(db: Session, payload: AppointmentCreate) -> Appointment:
    end_time = _add_30_minutes(payload.start_time)

    db_obj = Appointment(
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        title=payload.title,
        visit_date=payload.visit_date,
        start_time=payload.start_time,
        end_time=end_time,
        status=payload.status,
        created_at=datetime.utcnow(),
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get(db: Session, appointment_id: int) -> Optional[Appointment]:
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()


def list_appointments(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    start_date=None,
    end_date=None,
) -> List[Appointment]:
    q = db.query(Appointment)
    if start_date is not None:
        q = q.filter(Appointment.visit_date >= start_date)
    if end_date is not None:
        q = q.filter(Appointment.visit_date <= end_date)
    return (
        q.order_by(Appointment.visit_date, Appointment.start_time)
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_appointments(
    db: Session,
    *,
    start_date=None,
    end_date=None,
) -> int:
    q = db.query(Appointment)
    if start_date is not None:
        q = q.filter(Appointment.visit_date >= start_date)
    if end_date is not None:
        q = q.filter(Appointment.visit_date <= end_date)
    return q.count()


def update(
    db: Session,
    appointment_id: int,
    payload: AppointmentUpdate,
) -> Optional[Appointment]:
    obj = get(db, appointment_id)
    if not obj:
        return None

    data = payload.dict(exclude_unset=True)
    if "start_time" in data and data["start_time"] is not None:
        data["end_time"] = _add_30_minutes(data["start_time"])

    for field, value in data.items():
        setattr(obj, field, value)

    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, appointment_id: int) -> bool:
    obj = get(db, appointment_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
