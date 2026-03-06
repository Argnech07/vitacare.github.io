from sqlalchemy import Column, Integer, String, Boolean, Text, Date, DateTime,  func
from sqlalchemy.orm import relationship
from app.db import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    curp = Column(String, unique=True, nullable=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    city = Column(String, nullable=True)
    street = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    marital_status = Column(String, nullable=True)
    education = Column(String, nullable=True)
    occupation = Column(String, nullable=True)
    origin = Column(String, nullable=True)
    worker_type = Column(String, nullable=True)
    blood_type = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    profile_picture = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    vitals = relationship("Vitals", back_populates="patient", cascade="all, delete-orphan")
    medical_history = relationship(
        "PatientMedicalHistory",
        back_populates="patient",
        uselist=False,              # 1 registro por paciente
        cascade="all, delete-orphan",
    )

    appointments = relationship(
        "Appointment",
        back_populates="patient",
        cascade="all, delete-orphan",
    )