from sqlalchemy import Column, Integer, DateTime, Text, DECIMAL, String
from app.database import Base
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

class DetectionLog(Base):
    __tablename__ = "detection_logs_table"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(IST))
    detected_gear = Column(Text, nullable=False)  # Example: "Helmet, Vest"
    confidence_score = Column(DECIMAL, nullable=False)  # Detection confidence
    entry_allowance = Column(String(255), nullable=False)  # "Allowed" or "Denied"