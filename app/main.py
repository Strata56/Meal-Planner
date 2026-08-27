import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from contextlib import asynccontextmanager
from datetime import datetime
from bson import ObjectId
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config.db import connect_to_mongo, close_mongo_connection, create_indexes, get_db
from app.middleware.error_middleware import error_handling_middleware
from app.routes import (
    auth_routes,
    user_routes,
    ingredient_routes,
    recipe_routes,
    meal_plan_routes,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    await create_indexes()
    
    db = get_db()
    if db is not None:
        # Seed ingredients if empty
        ing_count = await db.ingredients.count_documents({})
        if ing_count == 0:
            default_ingredients = [
                {"name": "Chicken Breast", "calories_per_100g": 165.0, "protein_per_100g": 31.0, "serving_size_g": 100.0},
                {"name": "White Rice (Cooked)", "calories_per_100g": 130.0, "protein_per_100g": 2.7, "serving_size_g": 100.0},
                {"name": "Egg (Whole)", "calories_per_100g": 143.0, "protein_per_100g": 12.6, "serving_size_g": 100.0},
                {"name": "Oats (Dry)", "calories_per_100g": 389.0, "protein_per_100g": 16.9, "serving_size_g": 100.0},
                {"name": "Milk (Whole)", "calories_per_100g": 61.0, "protein_per_100g": 3.2, "serving_size_g": 100.0},
                {"name": "Broccoli", "calories_per_100g": 34.0, "protein_per_100g": 2.8, "serving_size_g": 100.0},
                {"name": "Salmon Filet", "calories_per_100g": 208.0, "protein_per_100g": 20.0, "serving_size_g": 100.0},
                {"name": "Peanut Butter", "calories_per_100g": 588.0, "protein_per_100g": 25.0, "serving_size_g": 100.0},
                {"name": "Banana", "calories_per_100g": 89.0, "protein_per_100g": 1.1, "serving_size_g": 100.0},
                {"name": "Whey Protein Powder", "calories_per_100g": 400.0, "protein_per_100g": 80.0, "serving_size_g": 30.0},
            ]
            await db.ingredients.insert_many(default_ingredients)
            print("Successfully seeded default nutrition ingredients database.")
            
        # Seed default recipes if empty
        rec_count = await db.recipes.count_documents({})
        if rec_count == 0:
            rice = await db.ingredients.find_one({"name": "White Rice (Cooked)"})
            oats = await db.ingredients.find_one({"name": "Oats (Dry)"})
            broccoli = await db.ingredients.find_one({"name": "Broccoli"})
            salmon = await db.ingredients.find_one({"name": "Salmon Filet"})
            pb = await db.ingredients.find_one({"name": "Peanut Butter"})
            banana = await db.ingredients.find_one({"name": "Banana"})
            whey = await db.ingredients.find_one({"name": "Whey Protein Powder"})
            
            if all([rice, oats, broccoli, salmon, pb, banana, whey]):
                default_recipes = [
                    {
                        "title": "Protein Banana Oatmeal",
                        "description": "High-protein morning oats topped with fresh banana and creamy peanut butter.",
                        "ingredients": [
                            {"ingredient_id": oats["_id"], "amount_g": 80.0},
                            {"ingredient_id": whey["_id"], "amount_g": 30.0},
                            {"ingredient_id": banana["_id"], "amount_g": 100.0},
                            {"ingredient_id": pb["_id"], "amount_g": 20.0}
                        ],
                        "instructions": [
                            "Boil 80g of dry oats in water or milk until soft.",
                            "Stir in one scoop (30g) of whey protein powder until smooth.",
                            "Slice a medium banana and place on top.",
                            "Drizzle with peanut butter and enjoy."
                        ],
                        "calories": 637.8,
                        "protein": 43.6,
                        "created_by": ObjectId("6a8878601fd1680d81daeb3b"),
                        "created_at": datetime.utcnow()
                    },
                    {
                        "title": "Grilled Salmon with Rice & Broccoli",
                        "description": "A clean, protein-packed lunch option featuring wild salmon, white rice, and steamed broccoli.",
                        "ingredients": [
                            {"ingredient_id": salmon["_id"], "amount_g": 150.0},
                            {"ingredient_id": rice["_id"], "amount_g": 150.0},
                            {"ingredient_id": broccoli["_id"], "amount_g": 100.0}
                        ],
                        "instructions": [
                            "Season the salmon fillet and pan-sear or grill until cooked through.",
                            "Steam 100g of fresh broccoli florets.",
                            "Plate the grilled salmon alongside cooked white rice and steamed broccoli."
                        ],
                        "calories": 541.0,
                        "protein": 36.9,
                        "created_by": ObjectId("6a8878601fd1680d81daeb3b"),
                        "created_at": datetime.utcnow()
                    }
                ]
                await db.recipes.insert_many(default_recipes)
                print("Successfully seeded default recipes database.")
            
    yield
    await close_mongo_connection()

app = FastAPI(
    title="Recipe Sharing & Meal Planner API",
    description="Backend API for recipe nutrition tracking and weekly meal slot scheduling.",
    version="1.0.0",
    lifespan=lifespan
)

app.middleware("http")(error_handling_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(ingredient_routes.router)
app.include_router(recipe_routes.router)
app.include_router(meal_plan_routes.router)

frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
os.makedirs(frontend_path, exist_ok=True)
app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

@app.get("/")
async def get_root():
    index_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Welcome to Recipe Sharing & Meal Planner API."}
