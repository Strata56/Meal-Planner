from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.py_object_id import PyObjectId

class RecipeIngredientIn(BaseModel):
    ingredient_id: PyObjectId
    amount_g: float = Field(..., gt=0.0)

class RecipeIngredientOut(BaseModel):
    ingredient_id: PyObjectId
    amount_g: float
    name: Optional[str] = None
    calories_per_100g: Optional[float] = None
    protein_per_100g: Optional[float] = None

class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: List[str] = Field(default_factory=list)

class RecipeCreate(RecipeBase):
    ingredients: List[RecipeIngredientIn] = Field(..., min_length=1)

class RecipeOut(RecipeBase):
    id: PyObjectId = Field(..., alias="_id")
    ingredients: List[RecipeIngredientOut] = Field(default_factory=list)
    calories: float
    protein: float
    created_by: PyObjectId
    created_at: datetime
    creator_name: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "json_encoders": {datetime: lambda dt: dt.isoformat()}
    }
