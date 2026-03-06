from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from app.db import Base

class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    license_number = Column(String, nullable=False)
    specialty = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    visit_diagnosis_id = Column(Integer, ForeignKey("visit_diagnoses.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    pdf_path = Column(String(255), nullable=True)  # Ruta del PDF guardado en el servidor
