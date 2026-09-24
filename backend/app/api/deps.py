from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.db.session import get_db
from app.core.config import settings
from app.models import User
from app.schemas.user import TokenData
from app.core.token_blacklist import is_token_blacklisted

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    # Reject tokens that have been explicitly revoked via /auth/logout
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # 'sub' is the RFC 7519 standard claim for the subject (user ID).
        # Fall back to 'email' for backwards-compatibility with old tokens.
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        organization_id: str = payload.get("organization_id")
        if user_id is None and email is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        token_data = TokenData(email=email, role=role, organization_id=organization_id)
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Primary-key lookup (O(1) indexed) when sub is present, email fallback otherwise
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
    else:
        user = db.query(User).filter(User.email == token_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


