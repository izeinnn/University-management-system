# University Management System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)](https://fastapi.tiangolo.com/)
[![SQLModel](https://img.shields.io/badge/SQLModel-Latest-red)](https://sqlmodel.tiangolo.com/)

A comprehensive university management system built with **FastAPI** and **SQLModel**, providing REST APIs for managing students, instructors, courses, and enrollments with role-based authentication.

## 📋 Features

- ✅ **JWT Authentication** with role-based access control
- ✅ **Student Management** - Complete CRUD operations
- ✅ **Instructor Management** - Profile and course assignment
- ✅ **Course Management** - Create courses with enrollment limits
- ✅ **Enrollment System** - Student course enrollment with grades
- ✅ **Role-based Permissions** - Admin, Instructor, Student roles
- ✅ **Interactive API Documentation** - Auto-generated Swagger docs
- ✅ **Database Relationships** - Proper foreign key constraints
- ✅ **Input Validation** - Pydantic models for data validation

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Web framework for building APIs |
| **SQLModel** | Database ORM and data validation |
| **SQLite** | Database (easily replaceable) |
| **JWT** | Authentication tokens |
| **Bcrypt** | Password hashing |
| **Pydantic** | Data validation |
| **Uvicorn** | ASGI server |

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd uni-mangment-sys
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Copy the `.env` file and modify the `SECRET_KEY` for production use
   - Update database settings if needed

5. **Initialize the database with sample data**:
   ```bash
   python init_db.py
   ```

## Running the Application

1. **Start the FastAPI server**:
   ```bash
   python main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload
   ```

2. **Access the application**:
   - API: http://localhost:8000
   - Interactive API Documentation: http://localhost:8000/docs
   - Alternative API Documentation: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user information

### Students
- `POST /students/` - Create a new student profile
- `GET /students/` - List all students (admin/instructor only)
- `GET /students/{student_id}` - Get specific student details
- `PUT /students/{student_id}` - Update student information
- `DELETE /students/{student_id}` - Delete student (admin only)
- `GET /students/{student_id}/enrollments` - Get student's enrollments

### Instructors
- `POST /instructors/` - Create instructor profile (admin only)
- `GET /instructors/` - List all instructors
- `GET /instructors/{instructor_id}` - Get specific instructor details
- `PUT /instructors/{instructor_id}` - Update instructor information
- `DELETE /instructors/{instructor_id}` - Delete instructor (admin only)
- `GET /instructors/{instructor_id}/courses` - Get instructor's courses

### Courses
- `POST /courses/` - Create new course (admin only)
- `GET /courses/` - List all courses
- `GET /courses/{course_id}` - Get specific course details
- `PUT /courses/{course_id}` - Update course information
- `DELETE /courses/{course_id}` - Delete course (admin only)
- `GET /courses/{course_id}/enrollments` - Get course enrollments

### Enrollments
- `POST /enrollments/` - Enroll student in course
- `GET /enrollments/` - List enrollments (with filters)
- `GET /enrollments/{enrollment_id}` - Get specific enrollment
- `PUT /enrollments/{enrollment_id}` - Update enrollment (grades, status)
- `DELETE /enrollments/{enrollment_id}` - Delete enrollment (admin only)

## User Roles and Permissions

### Admin
- Full access to all endpoints
- Can create, read, update, and delete all entities
- Can manage user accounts and system settings

### Instructor
- Can view all students and courses
- Can manage their own courses
- Can view and update enrollments for their courses
- Can assign grades to students

### Student
- Can view their own profile and enrollments
- Can enroll in available courses
- Can drop courses (update enrollment status)
- Limited access to other entities

## Authentication

To access protected endpoints:

1. Login using the `/auth/login` endpoint
2. Copy the returned access token
3. Include it in the Authorization header: `Bearer <your_token>`

## Database Schema

The system includes the following main entities:

- **Users**: Base user information with roles
- **Students**: Student-specific information linked to users
- **Instructors**: Instructor-specific information linked to users
- **Courses**: Course information with instructor assignments
- **Enrollments**: Student-course relationships with status and grades

## Configuration

Environment variables (in `.env` file):

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key (change in production!)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

