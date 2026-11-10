# backend/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.crud import authenticate_user
from backend.config import JWT_SECRET
from backend.database import get_db
from backend.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from passlib.hash import argon2

import jwt

router = APIRouter()

# ✅ Global password context — register & login both use this
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(password, hashed)
    except UnknownHashError:
        return False

class ResetPasswordRequest(BaseModel):
    username: str
    new_password: str

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter_by(username=user.username))
    db_user = result.scalar_one_or_none()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {"sub": db_user.username, "exp": datetime.utcnow() + timedelta(hours=12)}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # check if username already exists
    result = await db.execute(select(User).filter_by(username=user.username))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    # hash password
    hashed_password = hash_password(user.password)

    # create user
    db_user = User(username=user.username, password_hash=hashed_password)
    db.add(db_user)
    await db.commit()
    return {"msg": "User created"}

@router.post("/reset-password-direct")
async def reset_password_direct(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    # 1. Look up the user
    result = await db.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()

    # 2. If not found → clear error
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")

    # 3. Update password hash
    user.password_hash = argon2.hash(payload.new_password)
    await db.commit()

    return {"msg": "Password updated successfully"}