# Nourish | Recipe Sharing & Meal Planner

A simple and clean full-stack application built with FastAPI (Python) and local MongoDB to track custom recipe ingredient portions, compute calories and protein, and coordinate weekly planner slots.

## Project Structure
```text
recipe-meal-planner/
├── README.md
├── .vscode/
│   └── launch.json
├── backend/
│   ├── requirements.txt
│   ├── .env
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── config/
│       │   └── db.py
│       ├── middleware/
│       │   ├── auth_middleware.py
│       │   └── error_middleware.py
│       ├── models/
│       │   ├── py_object_id.py
│       │   ├── user.py
│       │   ├── ingredient.py
│       │   └── recipe.py
│       ├── controllers/
│       │   ├── auth_controller.py
│       │   ├── user_controller.py
│       │   ├── ingredient_controller.py
│       │   └── recipe_controller.py
│       └── utils/
│           └── nutrition_calculator.py
└── frontend/
    ├── index.html
    ├── style.css
    └── app.js
```

## Running the Application

### 1. Database Requirement
Ensure local MongoDB is running on your machine:
*   Default connection string: `mongodb://localhost:27017`

### 2. VS Code Launch (Recommended)
1.  Open the folder `C:\Users\HP\OneDrive\Documents\Meal Planner` in VS Code.
2.  Open the terminal (**Ctrl + `**) and install the requirements:
    ```bash
    pip install -r backend/requirements.txt
    ```
3.  Go to the **Run & Debug** sidebar tab (**Ctrl + Shift + D**), select **FastAPI: Meal Planner** from the dropdown, and press **F5**.
4.  Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

### 3. Manual Terminal Startup
If running directly from the command line:
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
Then visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
