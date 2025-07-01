# Quick Start Guide - University Management System

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Installation Steps

1. **Navigate to the project directory:**
   ```bash
   cd uni-mangment-sys
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate on Windows
   .venv\Scripts\activate
   
   # Activate on macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database:**
   ```bash
   python init_db.py
   ```

5. **Start the server:**
   ```bash
   python main.py
   ```
   
   Or using uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

## Quick Test

1. **Open your browser and go to:**
   - API Documentation: http://localhost:8000/docs
   - API: http://localhost:8000

2. **Test the API:**
   ```bash
   python test_api.py
   ```

## Default Login Credentials

- **Admin**: admin@university.edu / admin123
- **Instructor**: john.smith@university.edu / instructor123
- **Student**: alice.johnson@student.university.edu / student123

## Troubleshooting

If you encounter import errors:
1. Make sure you're in the correct directory
2. Ensure the virtual environment is activated
3. Reinstall dependencies: `pip install -r requirements.txt`

If the server doesn't start:
1. Check if port 8000 is available
2. Try a different port: `uvicorn main:app --port 8001`
3. Check the terminal for error messages

## Project Structure
```
uni-mangment-sys/
├── app/
│   ├── routes/
│   │   ├── auth.py
│   │   ├── students.py
│   │   ├── instructors.py
│   │   ├── courses.py
│   │   └── enrollments.py
│   ├── models.py
│   ├── auth.py
│   └── database.py
├── main.py
├── init_db.py
├── requirements.txt
├── .env
└── README.md
```
