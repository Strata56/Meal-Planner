from fastapi import APIRouter, Depends, Query
from app.controllers import meal_plan_controller
from app.middleware.auth_middleware import get_current_user
from app.models.meal_plan import MealPlanCreate, MealPlanDetailOut

router = APIRouter(prefix="/meal-plans", tags=["Meal Planner"])

@router.get("", response_model=MealPlanDetailOut)
async def get_weekly_plan(
    week_start_date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    current_user: dict = Depends(get_current_user)
):
    return await meal_plan_controller.get_meal_plan_by_week(current_user["_id"], week_start_date)

@router.post("", response_model=MealPlanDetailOut)
async def update_weekly_plan(
    plan: MealPlanCreate,
    current_user: dict = Depends(get_current_user)
):
    return await meal_plan_controller.upsert_meal_plan(current_user["_id"], plan)
