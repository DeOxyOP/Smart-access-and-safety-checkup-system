from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.camera_model import Camera

router = APIRouter()
india_timezone = timezone(timedelta(hours=5, minutes=30))

class CameraCreate(BaseModel):
    camera_name: str
    rtsp_url: str
    location: str

# ✅ Get all cameras (filtered by is_deleted=False)
@router.get("/get-cameras/")
def get_cameras(db: Session = Depends(get_db)):
    cameras = db.query(Camera).filter(Camera.is_deleted == False).all()
    if not cameras:
        return {"message": "No cameras available", "cameras": []}
    return cameras

# ✅ Add new camera (prevent duplicates)
@router.post("/cameras/")
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    existing_camera = db.query(Camera).filter(Camera.rtsp_url == camera.rtsp_url).first()
    
    if existing_camera:
        raise HTTPException(status_code=400, detail="Camera with this RTSP URL already exists!")

    new_camera = Camera(
        camera_name=camera.camera_name,
        location=camera.location,
        rtsp_url=camera.rtsp_url,
        created_on=datetime.now(india_timezone),
        modified_on=datetime.now(india_timezone),
        is_deleted=False
    )
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)
    
    return {"message": "Camera added successfully!"}
