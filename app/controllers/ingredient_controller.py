from typing import Optional
from fastapi import HTTPException, status
from bson import ObjectId
from app.config.db import get_db
from app.models.ingredient import IngredientCreate

async def create_ingredient(ingredient_in: IngredientCreate):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
        
    existing = await db.ingredients.find_one({"name": {"$regex": f"^{ingredient_in.name}$", "$options": "i"}})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ingredient with this name already exists")
        
    doc = ingredient_in.model_dump()
    result = await db.ingredients.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc

async def list_ingredients(search: Optional[str] = None):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
        
    query = {}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
        
    cursor = db.ingredients.find(query).sort("name", 1)
    return await cursor.to_list(200)

async def get_ingredient_by_id(ingredient_id: str):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
        
    try:
        oid = ObjectId(ingredient_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ingredient ID")
        
    ingredient = await db.ingredients.find_one({"_id": oid})
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient

async def delete_ingredient_by_id(ingredient_id: str):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
        
    try:
        oid = ObjectId(ingredient_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ingredient ID")
        
    result = await db.ingredients.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return None
