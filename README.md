# Nourish | Recipe Sharing & Meal Planner

A clean, responsive full-stack web application built with **FastAPI (Python)** and **MongoDB** to track custom recipe ingredient portions, compute calories and protein, and coordinate weekly meal planner slots.

---

## Features
- **Recipe Directory & Builder**: Create and browse recipes with custom ingredients and weights; calculates calories and protein automatically.
- **Weekly Meal Planner**: Assign recipes to breakfast, lunch, dinner, and snack slots for each day of the week.
- **Calorie & Protein Tracking**: Real-time progress bars comparing your planned intake against your daily nutritional goals.
- **Auto-Seeding**: Automatically seeds essential ingredients and sample recipes on first database connection.
- **Authentication**: JWT-based authentication for personal recipe and meal plan management.

---

## Project Structure
```text
Meal-Planner/
├── app/
│   ├── config/             # Database connection & settings
│   ├── controllers/        # Business logic for auth, recipes, meal plans
│   ├── middleware/         # Auth & error handling middleware
│   ├── models/             # Pydantic models & validation schemas
│   ├── routes/             # FastAPI route definitions
│   ├── utils/              # Nutrition calculations
│   └── main.py             # FastAPI entrypoint & static mounting
├── frontend/
│   ├── index.html          # Responsive single-page application
│   ├── style.css           # Clean styling & design system
│   └── app.js              # Client-side state & API communication
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── .python-version         # Python version for Render (3.11.9)
├── render.yaml             # Render Blueprint configuration
├── requirements.txt        # Python package dependencies
└── README.md
```

---

## Running Locally

### 1. Prerequisites
- Python 3.10+ installed
- MongoDB running locally on `mongodb://localhost:27017` (or a remote MongoDB Atlas URI)

### 2. Setup Virtual Environment
```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default local settings:
```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=recipe_planner_db
JWT_SECRET=your-secret-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 5. Start the Server
```bash
uvicorn app.main:app --reload --port 8000
```
Open your browser at **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.

---

## Deploying on Render

Render hosts the FastAPI web service, and MongoDB Atlas provides the free cloud database.

### Step 1: Set up MongoDB Atlas (Free Cloud Database)
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and create a free account.
2. Build a free shared cluster (M0).
3. Under **Database Access**, create a database user (username and password).
4. Under **Network Access**, click **Add IP Address** and choose **Allow Access From Anywhere** (`0.0.0.0/0`).
5. Go to **Databases** > **Connect** > **Drivers** > **Python**, and copy your connection string:
   ```text
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

### Step 2: Deploy on Render

#### Option A: Automatic via Render Blueprint (Recommended)
1. Push your repository to GitHub.
2. Go to your [Render Dashboard](https://dashboard.render.com).
3. Click **New +** > **Blueprint**.
4. Connect your `Meal-Planner` GitHub repository.
5. Render will automatically detect `render.yaml`.
6. When prompted, enter your `MONGO_URI` from MongoDB Atlas.
7. Click **Apply**. Render will build and deploy your app.

#### Option B: Manual Web Service Setup
1. On the Render Dashboard, click **New +** > **Web Service**.
2. Connect your GitHub repository (`Strata56/Meal-Planner`).
3. Set the following configuration:
   - **Name**: `meal-planner`
   - **Language / Runtime**: `Python`
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Under **Environment Variables**, add:
   - `PYTHON_VERSION`: `3.11.9`
   - `MONGO_URI`: `mongodb+srv://<user>:<password>@cluster0.xxx.mongodb.net/?retryWrites=true&w=majority`
   - `DB_NAME`: `recipe_planner_db`
   - `JWT_SECRET`: *(click Generate or enter a random secure string)*
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: `60`
5. Click **Create Web Service**.

Once deployed, Render gives you a public URL (e.g. `https://meal-planner-xxxx.onrender.com`).
