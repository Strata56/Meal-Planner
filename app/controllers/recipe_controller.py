from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from bson import ObjectId
from app.config.db import get_db
from app.models.recipe import RecipeCreate
from app.utils.nutrition_calculator import calculate_nutrition

async def create_recipe(recipe_in: RecipeCreate, user_id: ObjectId):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
        
    ingredients_list = [item.model_dump() for item in recipe_in.ingredients]
    nutrition = await calculate_nutrition(ingredients_list)
    
    doc = recipe_in.model_dump()
    for ing in doc["ingredients"]:
        ing["ingredient_id"] = ObjectId(ing["ingredient_id"])
        
    doc["calories"] = nutrition["calories"]
    doc["protein"] = nutrition["protein"]
    doc["created_by"] = user_id
    doc["created_at"] = datetime.utcnow()
    
    result = await db.recipes.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc

async def list_recipes(search: Optional[str] = None):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
        
    pipeline = [
        {
            "$lookup": {
                "from": "users",
                "localField": "created_by",
                "foreignField": "_id",
                "as": "creator"
            }
        },
        {
            "$project": {
                "_id": 1,
                "title": 1,
                "description": 1,
                "ingredients": 1,
                "instructions": 1,
                "calories": 1,
                "protein": 1,
                "created_by": 1,
                "created_at": 1,
                "creator_name": {"$arrayElemAt": ["$creator.username", 0]}
            }
        },
        {"$sort": {"created_at": -1}}
    ]
    
    if search:
        pipeline.insert(0, {"$match": {"title": {"$regex": search, "$options": "i"}}})
        
    cursor = db.recipes.aggregate(pipeline)
    return await cursor.to_list(100)

async def get_recipe_by_id(recipe_id: str):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
        
    try:
        oid = ObjectId(recipe_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid recipe ID")
        
    pipeline = [
        {"$match": {"_id": oid}},
        {
            "$unwind": {
                "path": "$ingredients",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$lookup": {
                "from": "ingredients",
                "localField": "ingredients.ingredient_id",
                "foreignField": "_id",
                "as": "ing_detail"
            }
        },
        {
            "$project": {
                "_id": 1,
                "title": 1,
                "description": 1,
                "instructions": 1,
                "calories": 1,
                "protein": 1,
                "created_by": 1,
                "created_at": 1,
                "ingredient_item": {
                    "ingredient_id": "$ingredients.ingredient_id",
                    "amount_g": "$ingredients.amount_g",
                    "name": {"$arrayElemAt": ["$ing_detail.name", 0]},
                    "calories_per_100g": {"$arrayElemAt": ["$ing_detail.calories_per_100g", 0]},
                    "protein_per_100g": {"$arrayElemAt": ["$ing_detail.protein_per_100g", 0]}
                }
            }
        },
        {
            "$group": {
                "_id": "$_id",
                "title": {"$first": "$title"},
                "description": {"$first": "$description"},
                "instructions": {"$first": "$instructions"},
                "calories": {"$first": "$calories"},
                "protein": {"$first": "$protein"},
                "created_by": {"$first": "$created_by"},
                "created_at": {"$first": "$created_at"},
                "ingredients": {"$push": "$ingredient_item"}
            }
        }
    ]
    
    cursor = db.recipes.aggregate(pipeline)
    results = await cursor.to_list(1)
    if not results:
        raise HTTPException(status_code=404, detail="Recipe not found")
        
    recipe = results[0]
    
    if recipe.get("ingredients") == [{}] or (len(recipe.get("ingredients", [])) == 1 and recipe["ingredients"][0].get("ingredient_id") is None):
        recipe["ingredients"] = []
        
    return recipe

async def delete_recipe_by_id(recipe_id: str, user_id: ObjectId):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
        
    try:
        oid = ObjectId(recipe_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid recipe ID")
        
    recipe = await db.recipes.find_one({"_id": oid})
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
        
    if recipe["created_by"] != user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this recipe")
        
    await db.recipes.delete_one({"_id": oid})
    return None
