from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.hierarchy import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token

class AuthService:
    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        user = db.query(User).filter(User.email == user_in.email).first()
        if user:
            raise HTTPException(status_code=400, detail="Email already registered")
            
        import uuid
        from app.core.security import decode_invite_token
        
        org_id = None
        assigned_role = "INSPECTOR"
        if user_in.invite_token:
            decoded_org = decode_invite_token(user_in.invite_token)
            if not decoded_org:
                raise HTTPException(status_code=400, detail="Invalid or expired invite token")
            org_id = decoded_org
        else:
            org_id = str(uuid.uuid4())
            
        # Use user_in.role if provided, otherwise default to ADMIN for new organizations
        assigned_role = user_in.role if user_in.role else "ADMIN"
            
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            full_name=user_in.full_name,
            email=user_in.email, 
            hashed_password=hashed_password,
            role=assigned_role,
            organization_id=org_id,
            organization_name=user_in.organization_name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_token_for_user(user: User):
        # Use 'sub' (RFC 7519 standard claim) as the primary user identifier.
        # This allows O(1) indexed DB lookup by primary key instead of a
        # string scan on the email column.
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "organization_id": str(user.organization_id)
        }
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
