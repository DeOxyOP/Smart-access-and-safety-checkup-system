import cv2
from ultralytics import YOLO
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models.camera_model import Camera
from app.routes import admin_routes, camera_routes, detection_logs_routes
import threading
import time

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_routes.router, prefix="/api")
app.include_router(camera_routes.router, prefix="/api")
app.include_router(detection_logs_routes.router, prefix="/api")

@app.get("/")
def home():
    return {"message": "Welcome to Helmet and Safety Vest Detection API"}

# Load the YOLO model
model = YOLO(r"C:\Users\jashk\Downloads\model\Yolov10m_LalaSet\weights\best.pt")

# Store camera instances and detection status
camera_dict = {}
detection_status = {}
detection_threads = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    """Fetch available cameras from the database on startup and initialize them."""
    db = SessionLocal()
    cameras = db.query(Camera).filter(Camera.is_deleted == False).all()
    db.close()

    for camera in cameras:
        camera_dict[camera.camera_id] = cv2.VideoCapture(0)  
        detection_status[camera.camera_id] = False  
    
    print(f"Initialized {len(camera_dict)} cameras.")

def detect_objects(camera_id):
    """Runs YOLO detection in a loop for the specified camera."""
    cap = camera_dict.get(camera_id)
    if not cap or not cap.isOpened():
        print(f"Camera {camera_id} not accessible.")
        return
    
    detection_status[camera_id] = True  

    while detection_status[camera_id]:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        results = model.predict(source=frame, conf=0.5, show=False)
        annotated_frame = results[0].plot()

        _, img_encoded = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = img_encoded.tobytes()

        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

    cap.release()
    del camera_dict[camera_id]  
    print(f"Camera {camera_id} released.")

@app.get("/start_detection")
async def start_detection(camera_id: int):
    """Start detection for a given camera ID."""
    if camera_id not in camera_dict:
        camera_dict[camera_id] = cv2.VideoCapture(0)  

    cap = camera_dict[camera_id]
    if not cap.isOpened():
        return {"error": "Camera not found or cannot be accessed"}

    detection_status[camera_id] = True  

    def generate():
        return detect_objects(camera_id)

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/stop_detection")
async def stop_detection(camera_id: int):
    """Stops detection and releases the camera."""
    if camera_id in detection_status:
        detection_status[camera_id] = False  

        cap = camera_dict.get(camera_id)
        if cap and cap.isOpened():
            cap.release()
            print(f"Camera {camera_id} released.")

    return {"error": "Camera not found or already stopped"}
