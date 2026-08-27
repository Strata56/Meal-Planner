from typing import List, Optional
from fastapi import APIRouter, Depends, status
from app.controllers import recipe_controller
from app.middleware.auth_middleware import get_current_user
from app.models.recipe import RecipeCreate, RecipeOut

router = APIRouter(prefix="/recipes", tags=["Recipes"])

@router.post("", response_model=RecipeOut, status_code=status.HTTP_201_CREATED)
async def create_new_recipe(
    recipe: RecipeCreate,
    current_user: dict = Depends(get_current_user)
):
    return await recipe_controller.create_recipe(recipe, current_user["_id"])

@router.get("", response_model=List[RecipeOut])
async def search_recipes(
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    return await recipe_controller.list_recipes(search)

@router.get("/{id}", response_model=RecipeOut)
async def get_recipe_details(
    id: str,
    current_user: dict = Depends(get_current_user)
):
    return await recipe_controller.get_recipe_by_id(id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    id: str,
    current_user: dict = Depends(get_current_user)
):
    return await recipe_controller.delete_recipe_by_id(id, current_user["_id"])
