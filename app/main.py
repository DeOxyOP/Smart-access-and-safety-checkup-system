import cv2
from ultralytics import YOLO
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models.camera_model import Camera
from app.routes import admin_routes, camera_routes, detection_logs_routes

Base.metadata.create_all(bind=engine)

app = FastAPI()

# ✅ Allow cross-origin requests from the React frontend
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

# ✅ Load the YOLO model
model = YOLO(r"D:\Major Project\trained_models\Yolov10m_LalaSet\weights\best.pt")

# ✅ Dictionary to store camera objects dynamically
camera_dict = {}

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
    cameras = db.query(Camera).filter(Camera.is_deleted == False).all()  # ✅ Only load active cameras
    db.close()
    
    for camera in cameras:
        camera_dict[camera.camera_id] = cv2.VideoCapture(0)
    
    print(f"Initialized {len(camera_dict)} cameras.")

@app.get("/start_detection")
async def start_detection(camera_id: int):
    cap = camera_dict.get(camera_id)
    if cap is None or not cap.isOpened():
        return {"error": "Camera not found or cannot be accessed"}

    def generate():
        while cap.isOpened():
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

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/stop_detection")
async def stop_detection(camera_id: int):
    cap = camera_dict.get(camera_id)
    if cap is not None and cap.isOpened():
        cap.release()
        del camera_dict[camera_id]  # ✅ Remove from dictionary
        return {"message": f"Detection stopped for camera {camera_id}"}
    return {"error": "Camera not found or already stopped"}
