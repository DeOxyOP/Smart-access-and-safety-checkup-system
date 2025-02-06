from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database import Base
from datetime import datetime, timezone
import bcrypt

class Admin(Base):
    __tablename__ = "admin_table"

    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # Store hashed password
    created_on = Column(DateTime, default=datetime.now(timezone.utc))
    modified_on = Column(DateTime, onupdate=datetime.now(timezone.utc))
    is_deleted = Column(Boolean, default=False)
    reset_token = Column(String(255), nullable=True)  # Add reset_token column

    # Method to check if password matches
    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))



