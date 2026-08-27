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

### 3. Manual Terminal Startup
If running directly from the command line:
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
Then visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
