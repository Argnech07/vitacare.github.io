from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Index

from app.db import Base


class PatientIncapacity(Base):
    __tablename__ = "patient_incapacities"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False)

    incapacity_for = Column(String(50), nullable=True)
    incapacity_type = Column(String(100), nullable=False)
    reason = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_incapacity_patient_created", "patient_id", "created_at"),
    )
