from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from app.db import Base

class VisitDiagnosis(Base):
    __tablename__ = "visit_diagnoses"
    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="CASCADE"), nullable=False)
    primary_diagnosis = Column(String(10), ForeignKey("cie10_diagnoses.code"), nullable=False)
    secondary_diagnoses = Column(JSONB, nullable=True)
    diagnosis_description = Column(Text, nullable=True)
