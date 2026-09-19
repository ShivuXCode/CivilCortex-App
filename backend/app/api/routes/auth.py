from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth_service import AuthService
from app.api.deps import get_current_user, oauth2_scheme, RoleChecker
from app.models import User
from app.core.limiter import limiter
from app.core.token_blacklist import blacklist_token

router = APIRouter()

@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
def register(request: Request, user_in: UserCreate, db: Session = Depends(get_db)):
    return AuthService.create_user(db, user_in)

@router.post("/invite")
@limiter.limit("5/minute")
def generate_invite(
    request: Request, 
    current_user: User = Depends(get_current_user)
):
    from app.core.security import create_invite_token
    token = create_invite_token(str(current_user.organization_id))
    return {"invite_token": token}

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = AuthService.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return AuthService.create_token_for_user(user)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
@limiter.limit("10/minute")
def logout(
    request: Request,
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user)
):
    """Revoke the current access token so it cannot be reused after logout."""
    blacklist_token(token)
    return {"message": "Successfully logged out"}

from pydantic import BaseModel, field_validator
class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=Token)
@limiter.limit("20/minute")
def refresh_token(request: Request, data: RefreshRequest, db: Session = Depends(get_db)):
    import jwt
    from app.core.config import settings
    try:
        payload = jwt.decode(data.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
            
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        return AuthService.create_token_for_user(user)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

class ForgotPasswordRequest(BaseModel):
    email: str

@router.post("/forgot-password")
@limiter.limit("5/minute")
def forgot_password(request: Request, data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        from app.core.security import create_password_reset_token
        import smtplib
        import os
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        reset_token = create_password_reset_token(user.email)
        reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
        
        smtp_host = os.environ.get("SMTP_HOST", "localhost")
        smtp_port = int(os.environ.get("SMTP_PORT", 1025))
        mail_from = os.environ.get("MAIL_FROM", "noreply@civilcortex.com")
        
        msg = MIMEMultipart()
        msg["From"] = mail_from
        msg["To"] = user.email
        msg["Subject"] = "CivilCortex Password Reset Request"
        
        body = f"""
        Hello,
        
        You requested a password reset for your CivilCortex account.
        Please click the link below to reset your password:
        
        {reset_link}
        
        If you did not request this, please ignore this email.
        """
        msg.attach(MIMEText(body, "plain"))
        
        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.send_message(msg)
            print(f"Successfully sent reset email to {user.email}")
        except Exception as e:
            print(f"Failed to send email: {e}")
            
    # Always return success to prevent email enumeration
    return {"message": "If the email is registered, a password reset link has been sent."}

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        import re
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

@router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(request: Request, data: ResetPasswordRequest, db: Session = Depends(get_db)):
    from app.core.security import verify_password_reset_token, get_password_hash
    email = verify_password_reset_token(data.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

class UserRoleUpdate(BaseModel):
    role: str

@router.patch("/users/{user_id}/role", response_model=UserResponse)
@limiter.limit("5/minute")
def update_user_role(
    request: Request,
    user_id: str, 
    data: UserRoleUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(RoleChecker(["ADMIN"]))
):
    if data.role not in ["INSPECTOR", "ENGINEER", "ADMIN"]:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if target_user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied. User belongs to a different organization.")
        
    target_user.role = data.role
    db.commit()
    db.refresh(target_user)
    return target_user

from typing import List

@router.get("/users", response_model=List[UserResponse])
def get_org_users(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Get all users in the current user's organization."""
    users = db.query(User).filter(User.organization_id == current_user.organization_id).all()
    return users
