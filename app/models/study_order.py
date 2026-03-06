from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date
from app.db import Base

class StudyOrder(Base):
    __tablename__ = "study_orders"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    order_date = Column(Date, nullable=False)
