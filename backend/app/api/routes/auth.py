from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth_service import AuthService
from app.api.deps import get_current_user, oauth2_scheme
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
