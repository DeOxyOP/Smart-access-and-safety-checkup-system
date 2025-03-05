from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.camera_model import Camera

router = APIRouter()
india_timezone = timezone(timedelta(hours=5, minutes=30))

class CameraCreate(BaseModel):
    camera_name: str
    rtsp_url: str
    location: str

# Get all cameras
@router.get("/get-cameras/")
def get_cameras(db: Session = Depends(get_db)):
    cameras = db.query(Camera).filter(Camera.is_deleted == False).all()
    if not cameras:
        return {"message": "No cameras available", "cameras": []}
    return cameras

# Add new camera
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


# Delete (soft delete) camera by ID
@router.delete("/cameras/{camera_id}/")
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    camera = db.query(Camera).filter(Camera.camera_id == camera_id, Camera.is_deleted == False).first()

    
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    camera.is_deleted = True
    camera.modified_on = datetime.now(india_timezone)
    
    db.commit()
    
    return {"message": f"Camera with ID {camera_id} deleted successfully!"}

