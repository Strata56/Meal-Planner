from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from app.models.py_object_id import PyObjectId

class UserGoals(BaseModel):
    calorie_goal: float = Field(default=2000.0)
    protein_goal: float = Field(default=150.0)

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserOut(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    username: str
    email: EmailStr
    goals: UserGoals = Field(default_factory=UserGoals)
    created_at: datetime

    model_config = {
        "populate_by_name": True,
        "json_encoders": {datetime: lambda dt: dt.isoformat()}
    }

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None
