from typing import List, Optional
from fastapi import APIRouter, Depends, status
from app.controllers import ingredient_controller
from app.middleware.auth_middleware import get_current_user
from app.models.ingredient import IngredientCreate, IngredientOut

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])

@router.post("", response_model=IngredientOut, status_code=status.HTTP_201_CREATED)
async def create_new_ingredient(
    ingredient: IngredientCreate,
    current_user: dict = Depends(get_current_user)
):
    return await ingredient_controller.create_ingredient(ingredient)

@router.get("", response_model=List[IngredientOut])
async def search_ingredients(
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    return await ingredient_controller.list_ingredients(search)

@router.get("/{id}", response_model=IngredientOut)
async def get_single_ingredient(
    id: str,
    current_user: dict = Depends(get_current_user)
):
    return await ingredient_controller.get_ingredient_by_id(id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_ingredient(
    id: str,
    current_user: dict = Depends(get_current_user)
):
    return await ingredient_controller.delete_ingredient_by_id(id)
