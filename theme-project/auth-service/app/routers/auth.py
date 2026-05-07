from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest, LoginRequest,
    TokenResponse, UserResponse, ValidateResponse
)

from app.services.auth import hash_password, verify_password, create_access_token, decode_token


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter_by(email=request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        email = request.email,
        password = hash_password(request.password),
        name = request.name
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user  = db.query(User).filter_by(User.email == request.email).first()

    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id), "email": user.email})

    return TokenResponse(access_token=access_token)



@router.get("/me", response_model=UserResponse)
def me(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Токен не передан")
 
    token = authorization.split(" ")[1]
    payload = decode_token(token)
 
    if not payload:
        raise HTTPException(status_code=401, detail="Токен недействителен")
 
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
 
    return user


@router.get("/validate", response_model=ValidateResponse)
def validate(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        return ValidateResponse(valid=False)
 
    token = authorization.split(" ")[1]
    payload = decode_token(token)
 
    if not payload:
        return ValidateResponse(valid=False)
 
    # Проверяем что пользователь ещё существует в БД
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        return ValidateResponse(valid=False)
 
    return ValidateResponse(
        valid=True,
        user_id=str(user.id),
        email=user.email,
    )