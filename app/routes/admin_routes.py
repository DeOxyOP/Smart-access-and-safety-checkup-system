from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.admin_models import Admin
from pydantic import BaseModel
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from fastapi.responses import JSONResponse
from typing import Optional
from jose import JWTError, jwt

# Secret key to encode JWT tokens
SECRET_KEY = "1234567890"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Function to create JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Function to verify JWT token
def verify_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

router = APIRouter()
india_timezone = timezone(timedelta(hours=5, minutes=30))

class LoginRequest(BaseModel):
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str
    
class ResetPasswordRequest(BaseModel):
    new_password: str

@router.get("/get-admins/")
def get_admins(db: Session = Depends(get_db)):
    return db.query(Admin).all()

@router.post("/admins/")
def create_admin(email: str, password: str, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    admin = Admin(email=email, password=hashed_password, created_on=datetime.now(india_timezone), modified_on=datetime.now(india_timezone), is_deleted=False)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@router.post("/admin/login")
def admin_login(request: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == request.email).first()
    if not admin or not admin.check_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login Successful"}

@router.post("/admin/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == request.email).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Email not found")
    reset_token = create_access_token(data={"sub": admin.email})
    reset_link = f"http://localhost:1234/reset-password?token={reset_token}"
    try:
        send_reset_email(admin.email, reset_link)
        return {"message": "Password reset instructions have been sent to your email."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

def send_reset_email(to_email: str, reset_link: str):
    from_email = "projectboss007@gmail.com"
    from_password = "ampn vikc hfyk hvwc"
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        msg = MIMEMultipart()
        msg['From'] = formataddr(('GG', from_email))
        msg['To'] = to_email
        msg['Subject'] = 'Password Reset Request'
        msg.attach(MIMEText(f"To reset your password, click on the following link: {reset_link}\n\nIf you did not request a password reset, please ignore this email.", 'plain'))
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print("Failed to send email:", e)
        raise Exception("Failed to send email.")

@router.post("/admin/reset-password")
def reset_password(request: ResetPasswordRequest, token: str = Query(...), db: Session = Depends(get_db)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(status_code=400, detail="Invalid token payload")
    admin = db.query(Admin).filter(Admin.email == user_email).first()
    if not admin:
        raise HTTPException(status_code=404, detail="User not found")
    admin.password = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.commit()
    return {"message": "Password reset successful"}



