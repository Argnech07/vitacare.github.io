from sqlalchemy import Column, Integer, String
from app.db import Base

class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True, index=True)
    generic_name = Column(String, nullable=False)
    brand_name = Column(String, nullable=True)
    form = Column(String, nullable=True)
    strength = Column(String, nullable=True)
