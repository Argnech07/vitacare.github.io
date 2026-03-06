from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, func, Index
from app.db import Base

class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True)
    date_id = Column(Integer, nullable=True)
    visit_ts = Column(DateTime(timezone=True), nullable=False, index=True)
    reason = Column(Text, nullable=True)
    exploration = Column(Text, nullable=True)
    therapeutic_plan = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Índice compuesto para optimizar búsquedas por paciente ordenadas por fecha
    __table_args__ = (
        Index('idx_visit_patient_date', 'patient_id', 'visit_ts'),
    )
