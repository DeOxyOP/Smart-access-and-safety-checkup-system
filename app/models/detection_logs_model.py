from sqlalchemy import Column, Integer, DateTime, Text, DECIMAL, String
from app.database import Base

class DetectionLog(Base):
    __tablename__ = "detection logs table"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    detected_gear = Column(Text)
    confidence_score = Column(DECIMAL)
    entry_allowance = Column(String(255))
