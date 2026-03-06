from sqlalchemy import Column, String, Text
from app.db import Base

class CIE10Diagnosis(Base):
    __tablename__ = "cie10_diagnoses"
    code = Column(String(10), primary_key=True)
    description = Column(Text, nullable=False)
    cie_group = Column(String(5), nullable=True)
    notes = Column(Text, nullable=True)
