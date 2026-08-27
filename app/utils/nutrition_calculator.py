from typing import List, Dict, Any
from fastapi import HTTPException
from bson import ObjectId
from app.config.db import get_db

async def calculate_nutrition(ingredients_list: List[Dict[str, Any]]) -> Dict[str, float]:
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
        
    total_calories = 0.0
    total_protein = 0.0
    
    if not ingredients_list:
        return {"calories": 0.0, "protein": 0.0}
        
    ing_ids = [ObjectId(item["ingredient_id"]) for item in ingredients_list]
    cursor = db.ingredients.find({"_id": {"$in": ing_ids}})
    db_ingredients = await cursor.to_list(len(ing_ids))
    
    ing_map = {str(ing["_id"]): ing for ing in db_ingredients}
    
    for item in ingredients_list:
        ing_id_str = str(item["ingredient_id"])
        amount_g = float(item["amount_g"])
        
        if ing_id_str in ing_map:
            db_ing = ing_map[ing_id_str]
            calories_per_100g = float(db_ing.get("calories_per_100g", 0.0))
            protein_per_100g = float(db_ing.get("protein_per_100g", 0.0))
            
            total_calories += (calories_per_100g / 100.0) * amount_g
            total_protein += (protein_per_100g / 100.0) * amount_g
            
    return {
        "calories": round(total_calories, 1),
        "protein": round(total_protein, 1)
    }
