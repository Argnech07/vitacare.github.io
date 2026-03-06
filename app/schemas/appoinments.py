# app/schemas/appointment.py
from datetime import date, time, datetime

from pydantic import BaseModel, Field

from app.models.appoinments import AppointmentStatus


class AppointmentBase(BaseModel):
    title: str | None = None
    visit_date: date
    start_time: time
    end_time: time | None = None
    status: AppointmentStatus = Field(default=AppointmentStatus.PENDING)


class AppointmentCreate(AppointmentBase):
    patient_id: int
    doctor_id: int


class AppointmentUpdate(BaseModel):
    title: str | None = None
    visit_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    status: AppointmentStatus | None = None
    doctor_id: int | None = None


class AppointmentOut(AppointmentBase):
    id: int
    patient_id: int
    doctor_id: int
    created_at: datetime

    class Config:
        from_attributes = True
