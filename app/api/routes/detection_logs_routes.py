from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.detection_logs_model import DetectionLog

router = APIRouter()

@router.get("/get-detection-logs/")
def get_detection_logs(db: Session = Depends(get_db)):
    logs = db.query(DetectionLog).all()
    return {"logs": logs}