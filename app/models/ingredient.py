from pydantic import BaseModel, Field
from app.models.py_object_id import PyObjectId

class IngredientBase(BaseModel):
    name: str
    calories_per_100g: float = Field(..., ge=0.0)
    protein_per_100g: float = Field(..., ge=0.0)
    serving_size_g: float = Field(default=100.0, ge=0.0)

class IngredientCreate(IngredientBase):
    pass

class IngredientOut(IngredientBase):
    id: PyObjectId = Field(..., alias="_id")

    model_config = {
        "populate_by_name": True
    }
