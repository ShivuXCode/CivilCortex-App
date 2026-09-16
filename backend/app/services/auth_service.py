from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.hierarchy import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token

class AuthService:
    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        user = db.query(User).filter(User.email == user_in.email).first()
        if user:
            raise HTTPException(status_code=400, detail="Email already registered")
        import uuid
        hashed_password = get_password_hash(user_in.password)
        org_id = str(uuid.uuid4())
        db_user = User(
            email=user_in.email, 
            hashed_password=hashed_password,
            role="INSPECTOR",
            organization_id=org_id
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
        access_token = create_access_token(data={
            "email": user.email,
            "role": user.role,
            "organization_id": user.organization_id
        })
        return {"access_token": access_token, "token_type": "bearer"}
