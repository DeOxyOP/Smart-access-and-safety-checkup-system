from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database import Base
from datetime import datetime, timezone

class Camera(Base):
    __tablename__ = 'camera_table'

    camera_id = Column(Integer, primary_key=True)
    camera_name = Column(String(255), nullable=False)
    rtsp_url = Column(String(255), nullable=False)
    created_on = Column(DateTime, nullable=False)
    modified_on = Column(DateTime)
    is_deleted = Column(Boolean, nullable=False)
    location = Column(String(255), nullable=False)  # Add the 'location' column
