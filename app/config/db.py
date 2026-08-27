import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "recipe_planner_db")
JWT_SECRET = os.getenv("JWT_SECRET", "a8b3cd43fe9b78e2d4e8c1b97a213e4bcf5f74bc7e4c5b3671249b2f34da19ff")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

class DatabaseHelper:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None

db_helper = DatabaseHelper()

def get_db():
    return db_helper.db

async def connect_to_mongo():
    db_helper.client = AsyncIOMotorClient(MONGO_URI)
    db_helper.db = db_helper.client[DB_NAME]
    print(f"Connected to MongoDB: {DB_NAME}")

async def close_mongo_connection():
    if db_helper.client:
        db_helper.client.close()
        print("Closed MongoDB connection")

async def create_indexes():
    db = db_helper.db
    if db is not None:
        await db.users.create_index("username", unique=True)
        await db.users.create_index("email", unique=True)
        await db.ingredients.create_index("name", unique=True)
        await db.meal_plans.create_index([("user_id", 1), ("week_start_date", 1)], unique=True)
        print("MongoDB unique constraints and index rules applied.")
