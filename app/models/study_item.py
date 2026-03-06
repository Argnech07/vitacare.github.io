from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date
from app.db import Base

class StudyItem(Base):
    __tablename__ = "study_items"
    id = Column(Integer, primary_key=True, index=True)
    study_order_id = Column(Integer, ForeignKey("study_orders.id", ondelete="CASCADE"), nullable=False)
    study_type = Column(String, nullable=False)
    assigned_doctor = Column(String(255), nullable=False, default="")
    name = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    document_date = Column(Date, nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    url = Column(Text, nullable=True)
