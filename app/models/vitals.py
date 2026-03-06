from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class Vitals(Base):
    __tablename__ = "vitals"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), index=True, nullable=False)

    taken_at = Column(DateTime, nullable=False)  # ya existe en la BD

    systolic = Column(Integer, nullable=True)
    diastolic = Column(Integer, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    respiratory_rate = Column(Integer, nullable=True)
    temperature = Column(Float, nullable=True)
    glucose = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)

    waist_cm = Column(Float, nullable=True)
    abdomen_cm = Column(Float, nullable=True)
    hip_cm = Column(Float, nullable=True)
    head_circumference_cm = Column(Float, nullable=True)

    patient = relationship("Patient", back_populates="vitals")
