from datetime import datetime
from fastapi import HTTPException
from bson import ObjectId
from app.config.db import get_db
from app.models.meal_plan import MealPlanCreate

async def get_meal_plan_by_week(user_id: ObjectId, week_start_date: str):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
        
    plan = await db.meal_plans.find_one({"user_id": user_id, "week_start_date": week_start_date})
    if not plan:
        return {
            "week_start_date": week_start_date,
            "meals": {
                day: {"breakfast": [], "lunch": [], "dinner": [], "snacks": []}
                for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            }
        }
        
    recipe_ids = set()
    meals_dict = plan.get("meals", {})
    for day, slots in meals_dict.items():
        for slot, ids in slots.items():
            for rid in ids:
                recipe_ids.add(ObjectId(rid) if isinstance(rid, str) else rid)
                
    if not recipe_ids:
        return format_plan_output(plan)
        
    recipes_cursor = db.recipes.find({"_id": {"$in": list(recipe_ids)}}, {"title": 1, "calories": 1, "protein": 1})
    recipes_list = await recipes_cursor.to_list(len(recipe_ids))
    recipe_map = {str(r["_id"]): {
        "id": str(r["_id"]),
        "title": r["title"],
        "calories": r.get("calories", 0.0),
        "protein": r.get("protein", 0.0)
    } for r in recipes_list}
    
    populated_meals = {}
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        day_slots = meals_dict.get(day, {"breakfast": [], "lunch": [], "dinner": [], "snacks": []})
        populated_meals[day] = {}
        for slot in ["breakfast", "lunch", "dinner", "snacks"]:
            slot_ids = day_slots.get(slot, [])
            populated_meals[day][slot] = [
                recipe_map[str(rid)] for rid in slot_ids if str(rid) in recipe_map
            ]
            
    plan["meals"] = populated_meals
    plan["_id"] = str(plan["_id"])
    plan["user_id"] = str(plan["user_id"])
    return plan

def format_plan_output(plan):
    formatted_meals = {}
    meals_dict = plan.get("meals", {})
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        day_slots = meals_dict.get(day, {"breakfast": [], "lunch": [], "dinner": [], "snacks": []})
        formatted_meals[day] = {}
        for slot in ["breakfast", "lunch", "dinner", "snacks"]:
            formatted_meals[day][slot] = [str(rid) for rid in day_slots.get(slot, [])]
    plan["meals"] = formatted_meals
    plan["_id"] = str(plan["_id"])
    plan["user_id"] = str(plan["user_id"])
    return plan

async def upsert_meal_plan(user_id: ObjectId, plan_in: MealPlanCreate):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
        
    doc_meals = {}
    for day, slots in plan_in.meals.items():
        doc_meals[day] = {}
        for slot, rids in slots.model_dump().items():
            doc_meals[day][slot] = [ObjectId(rid) for rid in rids]
            
    await db.meal_plans.update_one(
        {"user_id": user_id, "week_start_date": plan_in.week_start_date},
        {
            "$set": {
                "meals": doc_meals,
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    return await get_meal_plan_by_week(user_id, plan_in.week_start_date)
