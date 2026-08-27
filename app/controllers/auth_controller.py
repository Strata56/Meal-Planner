import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from app.config.db import get_db, JWT_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.user import UserCreate
from jose import jwt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")

async def register_user(user_in: UserCreate):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
        
    existing_username = await db.users.find_one({"username": {"$regex": f"^{user_in.username}$", "$options": "i"}})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    existing_email = await db.users.find_one({"email": {"$regex": f"^{user_in.email}$", "$options": "i"}})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    doc = {
        "username": user_in.username,
        "email": user_in.email,
        "hashed_password": hash_password(user_in.password),
        "goals": {"calorie_goal": 2000.0, "protein_goal": 150.0},
        "created_at": datetime.utcnow()
    }
    result = await db.users.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc

async def login_user(username_or_email: str, password: str):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
        
    user = await db.users.find_one({
        "$or": [
            {"username": {"$regex": f"^{username_or_email}$", "$options": "i"}},
            {"email": {"$regex": f"^{username_or_email}$", "$options": "i"}}
        ]
    })
    
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": user["username"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["username"]
    }
