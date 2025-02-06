from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.admin_models import Admin
from pydantic import BaseModel
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import random
import string
from fastapi.responses import JSONResponse
from urllib.parse import quote_plus

router = APIRouter()
india_timezone = timezone(timedelta(hours=5, minutes=30))

# Define LoginRequest model for validation
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

# Create a new admin (password will be hashed before storage)
@router.post("/admins/")
def create_admin(email: str, password: str, db: Session = Depends(get_db)):
    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    admin = Admin(
        email=email, 
        password=hashed_password.decode('utf-8'),  # Store the hashed password
        created_on=datetime.now(india_timezone), 
        modified_on=datetime.now(india_timezone), 
        is_deleted=False
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

# Admin login (using bcrypt to compare hashed passwords)
@router.post("/admin/login")
def admin_login(request: LoginRequest, db: Session = Depends(get_db)):
    # Fetch the admin from the database
    admin = db.query(Admin).filter(Admin.email == request.email).first()

    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Compare the provided password with the hashed password stored in the database
    if not admin.check_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login Successful"}

# Forgot Password route
@router.post("/admin/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Check if the email exists in the database
    admin = db.query(Admin).filter(Admin.email == request.email).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Email not found")

    # Generate a password reset token
    reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    # In a real application, you should store this token in the database and set an expiration date.

    # Generate the reset password link
    reset_link = f"http://localhost:1234/reset-password?token={reset_token}"

    # Send the reset email
    try:
        send_reset_email(admin.email, reset_link)
        return {"message": "Password reset instructions have been sent to your email."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error sending email: " + str(e))

# Function to send reset email
def send_reset_email(to_email: str, reset_link: str):
    from_email = "projectboss007@gmail.com"  # Replace with your email
    from_password = "ampn vikc hfyk hvwc"  # Replace with your email password or an app password

    # Set up the SMTP server (using Gmail as an example)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)

        msg = MIMEMultipart()
        msg['From'] = formataddr(('Your App Name', from_email))
        msg['To'] = to_email
        msg['Subject'] = 'Password Reset Request'

        # Compose the email body
        body = f"To reset your password, click on the following link: {reset_link}\n\nIf you did not request a password reset, please ignore this email."
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

    except Exception as e:
        print("Failed to send email:", e)
        raise Exception("Failed to send email.")

@router.post("/admin/reset-password")
def reset_password(token: str, request: ResetPasswordRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.reset_token == token).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    # Check if the token has expired
    if datetime.now(india_timezone) > admin.reset_token_expiry:
        raise HTTPException(status_code=400, detail="Token has expired")

    hashed_password = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt())
    admin.password = hashed_password.decode('utf-8')
    admin.reset_token = None  # Clear the reset token
    admin.reset_token_expiry = None  # Clear the expiration time
    db.commit()

    return {"message": "Password reset successful"}


