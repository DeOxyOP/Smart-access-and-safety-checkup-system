# detection happening on backend on another thread


# import cv2
# from ultralytics import YOLO
# from fastapi import FastAPI
# from fastapi.responses import StreamingResponse
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import Session
# from app.database import Base, engine, SessionLocal
# from app.models.camera_model import Camera
# from app.models.detection_logs_model import DetectionLog
# from app.routes import admin_routes, camera_routes, detection_logs_routes
# import threading
# import time

# Base.metadata.create_all(bind=engine)

# app = FastAPI()

# # ✅ Allow cross-origin requests
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Update for production security
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(admin_routes.router, prefix="/api")
# app.include_router(camera_routes.router, prefix="/api")
# app.include_router(detection_logs_routes.router, prefix="/api")

# @app.get("/")
# def home():
#     return {"message": "Welcome to Helmet and Safety Vest Detection API"}

# # ✅ Load the YOLO model
# model = YOLO(r"C:\Users\jashk\Downloads\model\Yolov10m_LalaSet\weights\best.pt")

# # ✅ Store camera instances and detection status
# camera_dict = {}
# detection_status = {}

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @app.on_event("startup")
# async def startup_event():
#     """Fetch available cameras from the database on startup and initialize them."""
#     db = SessionLocal()
#     cameras = db.query(Camera).filter(Camera.is_deleted == False).all()
#     db.close()

#     for camera in cameras:
#         camera_dict[camera.camera_id] = cv2.VideoCapture(0)  
#         detection_status[camera.camera_id] = False  
    
#     print(f"Initialized {len(camera_dict)} cameras.")

# def detect_objects(camera_id):
#     """Runs YOLO detection every 5 seconds for the specified camera."""
#     cap = camera_dict.get(camera_id)
#     if not cap or not cap.isOpened():
#         print(f"Camera {camera_id} not accessible.")
#         return

#     detection_status[camera_id] = True

#     while detection_status[camera_id]:
#         start_time = time.time()  # Record the start time of detection

#         ret, frame = cap.read()
#         if not ret:
#             break

#         frame = cv2.flip(frame, 1)
#         results = model.predict(source=frame, conf=0.5, show=False)
        
#         # ✅ Extract detection results
#         detected_classes = [results[0].names[int(cls)] for cls in results[0].boxes.cls]
#         detected_gear = ", ".join(set(detected_classes)) if detected_classes else "No detection"

#         confidence_scores = results[0].boxes.conf.tolist()
#         confidence_score = max(confidence_scores) if confidence_scores else 0.0

#         entry_allowance = "Allowed" if "Helmet" in detected_gear and "Safety-Vest" in detected_gear else "Denied"

#         # ✅ Store detection logs in the database
#         db = SessionLocal()
#         new_log = DetectionLog(
#             camera_id=camera_id,
#             detected_gear=detected_gear,
#             confidence_score=confidence_score,
#             entry_allowance=entry_allowance
#         )
#         db.add(new_log)
#         db.commit()
#         db.close()

#         elapsed_time = time.time() - start_time
#         if elapsed_time < 5:
#             time.sleep(5 - elapsed_time)

#     print(f"Detection for camera {camera_id} stopped.")

# def stream_video(camera_id):
#     """Continuously streams video for the specified camera."""
#     cap = camera_dict.get(camera_id)
#     if not cap or not cap.isOpened():
#         print(f"Camera {camera_id} not accessible.")
#         return

#     while detection_status.get(camera_id, False):
#         ret, frame = cap.read()
#         if not ret:
#             break

#         frame = cv2.flip(frame, 1)
#         _, img_encoded = cv2.imencode('.jpg', frame)
#         frame_bytes = img_encoded.tobytes()

#         yield (b'--frame\r\n'
#             b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

#     cap.release()
#     del camera_dict[camera_id]
#     print(f"Camera {camera_id} released.")

# @app.get("/start_detection")
# async def start_detection(camera_id: int):
#     """Start detection and streaming for a given camera ID."""
#     if camera_id not in camera_dict:
#         camera_dict[camera_id] = cv2.VideoCapture(0)  # Replace with actual camera ID if needed

#     cap = camera_dict[camera_id]
#     if not cap.isOpened():
#         return {"error": "Camera not found or cannot be accessed"}

#     if detection_status.get(camera_id, False):
#         return {"message": "Detection already running for this camera"}

#     detection_status[camera_id] = True

#     # Start detection in a separate thread
#     detection_thread = threading.Thread(target=detect_objects, args=(camera_id,))
#     detection_thread.start()

#     # Stream video
#     def generate():
#         return stream_video(camera_id)

#     return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

# @app.get("/stop_detection")
# async def stop_detection(camera_id: int):
#     """Stops detection and releases the camera."""
#     if camera_id in detection_status:
#         detection_status[camera_id] = False  

#         cap = camera_dict.get(camera_id)
#         if cap and cap.isOpened():
#             cap.release()
#             print(f"Camera {camera_id} released.")

#     return {"message": "Detection stopped for camera {camera_id}"}



# detection and video with 2.5 seconds interval

import cv2
from ultralytics import YOLO
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.db.database import Base, engine, SessionLocal
from app.db.models.camera_model import Camera
from app.db.models.detection_logs_model import DetectionLog
from app.api.routes import admin_routes, camera_routes, detection_logs_routes
import threading
import time

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

model = YOLO(r"C:\Users\jashk\Downloads\model\yolov8m_Lalaset\weights\best.pt")

camera_dict = {}
detection_status = {}
detection_threads = {}
last_detection_result = {}  
lock = threading.Lock()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    """Initialize cameras on application startup."""
    db = SessionLocal()
    cameras = db.query(Camera).filter(Camera.is_deleted == False).all()
    db.close()

    for camera in cameras:
        camera_dict[camera.camera_id] = cv2.VideoCapture(0)
        detection_status[camera.camera_id] = True
        last_detection_result[camera.camera_id] = {"gear": "No detection", "confidence": 0.0, "entry": "Denied"}


def run_detection(camera_id):
    """Runs object detection in a separate thread."""
    cap = camera_dict.get(camera_id)
    if not cap or not cap.isOpened():
        print(f"Camera {camera_id} is not accessible.")
        return

    while detection_status[camera_id]:
        time.sleep(2.5)  # Wait for 5 seconds between detections

        # Read frame for detection
        ret, frame = cap.read()
        if not ret:
            continue

        # Flip the frame horizontally for detection
        frame = cv2.flip(frame, 1)

        # Use lower resolution for detection
        resized_frame = cv2.resize(frame, (640, 480))

        # Run YOLO detection
        results = model.predict(source=resized_frame, conf=0.5, show=False)
        detected_classes = [results[0].names[int(cls)] for cls in results[0].boxes.cls]
        detected_gear = ", ".join(set(detected_classes)) if detected_classes else "No detection"

        confidence_scores = results[0].boxes.conf.tolist()
        confidence_score = max(confidence_scores) if confidence_scores else 0.0
        entry_allowance = "Allowed" if "Helmet" in detected_gear and "Safety-Vest" in detected_gear else "Denied"

        # Update the detection results
        with lock:
            last_detection_result[camera_id] = {
                "gear": detected_gear,
                "confidence": confidence_score,
                "entry": entry_allowance,
            }

        # Log detection in the database
        db = SessionLocal()
        new_log = DetectionLog(
            camera_id=camera_id,
            detected_gear=detected_gear,
            confidence_score=confidence_score,
            entry_allowance=entry_allowance,
        )
        db.add(new_log)
        db.commit()
        db.close()


@app.get("/start_detection")
async def start_detection(camera_id: int):
    """Start video streaming and detection for a given camera."""
    if camera_id not in camera_dict:
        camera_dict[camera_id] = cv2.VideoCapture(0)

    cap = camera_dict[camera_id]
    if not cap.isOpened():
        return {"error": "Camera not found or cannot be accessed"}

    detection_status[camera_id] = True

    # Start detection thread
    if camera_id not in detection_threads:
        detection_thread = threading.Thread(target=run_detection, args=(camera_id,), daemon=True)
        detection_threads[camera_id] = detection_thread
        detection_thread.start()

    def generate():
        while detection_status[camera_id]:
            ret, frame = cap.read()
            if not ret:
                break

            # Flip the frame horizontally for streaming
            frame = cv2.flip(frame, 1)

            # Overlay detection results
            with lock:
                detection_result = last_detection_result.get(camera_id, {})
                detected_gear = detection_result.get("gear", "No detection")
                confidence = detection_result.get("confidence", 0.0)
                entry = detection_result.get("entry", "Denied")

            # Add detection results to the frame
            cv2.putText(frame, f"Gear: {detected_gear}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Confidence: {confidence:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Entry: {entry}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            _, img_encoded = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + img_encoded.tobytes() + b'\r\n')

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/stop_detection")
async def stop_detection(camera_id: int):
    """Stops video streaming and detection for a given camera."""
    detection_status[camera_id] = False
    cap = camera_dict.get(camera_id)
    if cap and cap.isOpened():
        cap.release()
    return {"message": f"Detection stopped for camera {camera_id}"}
