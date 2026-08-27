from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from app.models.py_object_id import PyObjectId

class DailyMeals(BaseModel):
    breakfast: List[PyObjectId] = Field(default_factory=list)
    lunch: List[PyObjectId] = Field(default_factory=list)
    dinner: List[PyObjectId] = Field(default_factory=list)
    snacks: List[PyObjectId] = Field(default_factory=list)

class MealPlanBase(BaseModel):
    week_start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    meals: Dict[str, DailyMeals] = Field(default_factory=dict)

class MealPlanCreate(MealPlanBase):
    pass

class MealPlanOut(MealPlanBase):
    id: PyObjectId = Field(..., alias="_id")
    user_id: PyObjectId
    created_at: datetime

    model_config = {
        "populate_by_name": True,
        "json_encoders": {datetime: lambda dt: dt.isoformat()}
    }

class RecipeBrief(BaseModel):
    id: str
    title: str
    calories: float
    protein: float

class DailyMealsDetail(BaseModel):
    breakfast: List[RecipeBrief] = Field(default_factory=list)
    lunch: List[RecipeBrief] = Field(default_factory=list)
    dinner: List[RecipeBrief] = Field(default_factory=list)
    snacks: List[RecipeBrief] = Field(default_factory=list)

class MealPlanDetailOut(BaseModel):
    week_start_date: str
    meals: Dict[str, DailyMealsDetail] = Field(default_factory=dict)
