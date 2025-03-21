# import cv2
# from ultralytics import YOLO
# from fastapi import FastAPI, Depends
# from fastapi.responses import StreamingResponse
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import Session
# from app.db.database import Base, engine, SessionLocal
# from app.db.models.camera_model import Camera
# from app.db.models.detection_logs_model import DetectionLog
# from app.api.routes import admin_routes, camera_routes, detection_logs_routes
# import threading
# import time

# Base.metadata.create_all(bind=engine)

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
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

# model = YOLO(r"C:\Users\jashk\Downloads\model\Yolov10m_LalaSet\weights\best.pt")

# camera_dict = {}
# detection_status = {}
# detection_threads = {}
# last_detection_result = {}  
# lock = threading.Lock()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @app.on_event("startup")
# async def startup_event():
#     db = SessionLocal()
#     cameras = db.query(Camera).filter(Camera.is_deleted == False).all()
#     db.close()

#     for camera in cameras:
#         camera_dict[camera.camera_id] = cv2.VideoCapture(0)
#         detection_status[camera.camera_id] = True
#         last_detection_result[camera.camera_id] = {"gear": "No detection", "confidence": 0.0, "entry": "Denied", "boxes": []}

# def run_detection(camera_id):
#     cap = camera_dict.get(camera_id)
#     if not cap or not cap.isOpened():
#         print(f"Camera {camera_id} is not accessible.")
#         return

#     while detection_status[camera_id]:
#         time.sleep(2.5)
#         ret, frame = cap.read()
#         if not ret:
#             continue

#         frame = cv2.flip(frame, 1)
#         results = model.predict(source=frame, conf=0.5, show=False)

#         detected_boxes = []
#         for box, cls, conf in zip(results[0].boxes.xyxy, results[0].boxes.cls, results[0].boxes.conf):
#             x1, y1, x2, y2 = map(int, box)
#             class_name = results[0].names[int(cls)]
#             confidence = float(conf)
#             detected_boxes.append((x1, y1, x2, y2, class_name, confidence))

#         detected_gear = ", ".join(set([box[4] for box in detected_boxes])) if detected_boxes else "No detection"
#         confidence_score = max([box[5] for box in detected_boxes]) if detected_boxes else 0.0
#         entry_allowance = "Allowed" if "Helmet" in detected_gear and "Safety-Vest" in detected_gear else "Denied"

#         with lock:
#             last_detection_result[camera_id] = {
#                 "gear": detected_gear,
#                 "confidence": confidence_score,
#                 "entry": entry_allowance,
#                 "boxes": detected_boxes,
#             }

#         db = SessionLocal()
#         new_log = DetectionLog(
#             camera_id=camera_id,
#             detected_gear=detected_gear,
#             confidence_score=confidence_score,
#             entry_allowance=entry_allowance,
#         )
#         db.add(new_log)
#         db.commit()
#         db.close()

# @app.get("/start_detection")
# async def start_detection(camera_id: int):
#     if camera_id not in camera_dict:
#         camera_dict[camera_id] = cv2.VideoCapture(0)

#     cap = camera_dict[camera_id]
#     if not cap.isOpened():
#         return {"error": "Camera not found or cannot be accessed"}

#     detection_status[camera_id] = True

#     if camera_id not in detection_threads:
#         detection_thread = threading.Thread(target=run_detection, args=(camera_id,), daemon=True)
#         detection_threads[camera_id] = detection_thread
#         detection_thread.start()

#     def generate():
#         while detection_status[camera_id]:
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             frame = cv2.flip(frame, 1)
#             with lock:
#                 detection_result = last_detection_result.get(camera_id, {})
#                 detected_gear = detection_result.get("gear", "No detection")
#                 confidence = detection_result.get("confidence", 0.0)
#                 entry = detection_result.get("entry", "Denied")
#                 detected_boxes = detection_result.get("boxes", [])

#             for (x1, y1, x2, y2, class_name, conf) in detected_boxes:
#                 color = (0, 255, 0) if class_name in ["Helmet", "Safety-Vest"] else (0, 0, 255)
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#                 label = f"{class_name} ({conf:.2f})"
#                 cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

#             cv2.putText(frame, f"Gear: {detected_gear}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
#             cv2.putText(frame, f"Confidence: {confidence:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
#             cv2.putText(frame, f"Entry: {entry}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

#             _, img_encoded = cv2.imencode('.jpg', frame)
#             yield (b'--frame\r\n'
#                 b'Content-Type: image/jpeg\r\n\r\n' + img_encoded.tobytes() + b'\r\n')

#     return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

# @app.get("/stop_detection")
# async def stop_detection(camera_id: int):
#     detection_status[camera_id] = False
#     cap = camera_dict.get(camera_id)
#     if cap and cap.isOpened():
#         cap.release()
#     return {"message": f"Detection stopped for camera {camera_id}"}
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
    return {"message": "Welcome to Helmet, Safety Vest, and Mask Detection API"}

# Load Models
helmet_vest_model = YOLO(r"C:\Users\jashk\Downloads\model\Yolov10m_LalaSet\weights\best.pt")
mask_model = YOLO(r"C:\Users\jashk\Downloads\mask_best_80.pt")

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
    db = SessionLocal()
    cameras = db.query(Camera).filter(Camera.is_deleted == False).all()
    db.close()

    for camera in cameras:
        camera_dict[camera.camera_id] = cv2.VideoCapture(0)
        detection_status[camera.camera_id] = True
        last_detection_result[camera.camera_id] = {
            "gear": "No detection",
            "confidence": 0.0,
            "entry": "Denied",
            "boxes": []
        }

def run_detection(camera_id):
    cap = camera_dict.get(camera_id)
    if not cap or not cap.isOpened():
        print(f"Camera {camera_id} is not accessible.")
        return

    while detection_status[camera_id]:
        time.sleep(2.5)
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)

        # Run detections
        results_helmet_vest = helmet_vest_model.predict(source=frame, conf=0.5, show=False)
        results_mask = mask_model.predict(source=frame, conf=0.5, show=False)

        detected_boxes = []
        
        # Process Helmet/Vest Detections
        for box, cls, conf in zip(results_helmet_vest[0].boxes.xyxy, results_helmet_vest[0].boxes.cls, results_helmet_vest[0].boxes.conf):
            x1, y1, x2, y2 = map(int, box)
            class_name = results_helmet_vest[0].names[int(cls)]
            confidence = float(conf)
            detected_boxes.append((x1, y1, x2, y2, class_name, confidence))

        # Process Mask Detections
        for box, cls, conf in zip(results_mask[0].boxes.xyxy, results_mask[0].boxes.cls, results_mask[0].boxes.conf):
            x1, y1, x2, y2 = map(int, box)
            class_name = results_mask[0].names[int(cls)]
            confidence = float(conf)
            detected_boxes.append((x1, y1, x2, y2, class_name, confidence))

        detected_gear = ", ".join(set([box[4] for box in detected_boxes])) if detected_boxes else "No detection"
        confidence_score = max([box[5] for box in detected_boxes]) if detected_boxes else 0.0

        # Entry is allowed only if Helmet, Safety-Vest, and Mask are present
        if "Helmet" in detected_gear and "Safety-Vest" in detected_gear and "Mask" in detected_gear:
            entry_allowance = "Allowed"
        else:
            entry_allowance = "Denied"

        with lock:
            last_detection_result[camera_id] = {
                "gear": detected_gear,
                "confidence": confidence_score,
                "entry": entry_allowance,
                "boxes": detected_boxes,
            }

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
    if camera_id not in camera_dict:
        camera_dict[camera_id] = cv2.VideoCapture(0)

    cap = camera_dict[camera_id]
    if not cap.isOpened():
        return {"error": "Camera not found or cannot be accessed"}

    detection_status[camera_id] = True

    if camera_id not in detection_threads:
        detection_thread = threading.Thread(target=run_detection, args=(camera_id,), daemon=True)
        detection_threads[camera_id] = detection_thread
        detection_thread.start()

    def generate():
        while detection_status[camera_id]:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            with lock:
                detection_result = last_detection_result.get(camera_id, {})
                detected_gear = detection_result.get("gear", "No detection")
                confidence = detection_result.get("confidence", 0.0)
                entry = detection_result.get("entry", "Denied")
                detected_boxes = detection_result.get("boxes", [])

            for (x1, y1, x2, y2, class_name, conf) in detected_boxes:
                color = (0, 255, 0) if class_name in ["Helmet", "Safety-Vest", "Mask"] else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                label = f"{class_name} ({conf:.2f})"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            cv2.putText(frame, f"Gear: {detected_gear}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Confidence: {confidence:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Entry: {entry}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            _, img_encoded = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + img_encoded.tobytes() + b'\r\n')

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/stop_detection")
async def stop_detection(camera_id: int):
    detection_status[camera_id] = False
    cap = camera_dict.get(camera_id)
    if cap and cap.isOpened():
        cap.release()
    return {"message": f"Detection stopped for camera {camera_id}"}
