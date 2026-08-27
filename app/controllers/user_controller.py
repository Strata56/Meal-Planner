from fastapi import HTTPException
from app.config.db import get_db
from app.models.user import UserGoals

async def get_user_profile(current_user: dict):
    profile = current_user.copy()
    profile.pop("hashed_password", None)
    profile["_id"] = str(profile["_id"])
    return profile

async def update_user_goals(current_user: dict, goals: UserGoals):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
        
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"goals": goals.model_dump()}}
    )
    
    updated = await db.users.find_one({"_id": current_user["_id"]})
    updated.pop("hashed_password", None)
    updated["_id"] = str(updated["_id"])
    return updated
