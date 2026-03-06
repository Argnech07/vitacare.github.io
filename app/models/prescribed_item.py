from sqlalchemy import Column, Integer, Text, ForeignKey, String
from app.db import Base

class PrescribedItem(Base):
    __tablename__ = "prescribed_items"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(
        Integer,
        ForeignKey("prescriptions.id", ondelete="CASCADE"),
        nullable=False,
    )
    medication_id = Column(
        Integer,
        ForeignKey("medications.id", ondelete="CASCADE"),
        nullable=True,
    )
    medication_name = Column(Text, nullable=True)
    presentation = Column(Text, nullable=True)
    route = Column(String(30), nullable=True)
    frequency_hours = Column(Integer, nullable=True)
    duration_days = Column(Integer, nullable=True)
    duration_unit = Column(String(10), nullable=True)
    dosage = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
