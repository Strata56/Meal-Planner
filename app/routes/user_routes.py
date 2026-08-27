from fastapi import APIRouter, Depends
from app.controllers import user_controller
from app.middleware.auth_middleware import get_current_user
from app.models.user import UserGoals

router = APIRouter(prefix="/user", tags=["User Profile"])

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return await user_controller.get_user_profile(current_user)

@router.patch("/goals")
async def update_goals(goals: UserGoals, current_user: dict = Depends(get_current_user)):
    return await user_controller.update_user_goals(current_user, goals)
