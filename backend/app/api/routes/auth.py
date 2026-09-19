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

from pydantic import BaseModel
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
        reset_token = create_password_reset_token(user.email)
        # In a real app, send an email here. For now, print to console.
        print(f"PASSWORD RESET LINK FOR {user.email}: http://localhost:5173/reset-password?token={reset_token}")
    # Always return success to prevent email enumeration
    return {"message": "If the email is registered, a password reset link has been sent."}

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

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
