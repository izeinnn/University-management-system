from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List
from app.models import (
    Instructor,
    InstructorCreate,
    InstructorRead,
    InstructorUpdate,
    User,
    UserRole,
    Course,
    CourseRead,
)
from app.database import get_session
from app.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=InstructorRead)
async def create_instructor(
    instructor_data: InstructorCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    # Only admins can create instructors
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create instructor profile",
        )

    # Check if employee_id already exists
    existing_instructor = session.exec(
        select(Instructor).where(Instructor.employee_id == instructor_data.employee_id)
    ).first()
    if existing_instructor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Employee ID already exists"
        )

    # Check if user exists and has instructor role
    user = session.exec(select(User).where(User.id == instructor_data.user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user.role != UserRole.INSTRUCTOR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have instructor role",
        )

    db_instructor = Instructor(**instructor_data.dict())
    session.add(db_instructor)
    session.commit()
    session.refresh(db_instructor)

    return db_instructor


@router.get("/", response_model=List[InstructorRead])
async def get_instructors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    instructors = session.exec(select(Instructor).offset(skip).limit(limit)).all()
    return instructors


@router.get("/{instructor_id}", response_model=InstructorRead)
async def get_instructor(
    instructor_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    instructor = session.exec(
        select(Instructor).where(Instructor.id == instructor_id)
    ).first()
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found"
        )

    return instructor


@router.put("/{instructor_id}", response_model=InstructorRead)
async def update_instructor(
    instructor_id: int,
    instructor_update: InstructorUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    instructor = session.exec(
        select(Instructor).where(Instructor.id == instructor_id)
    ).first()
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found"
        )

    # Check if user is admin or the instructor themselves
    if current_user.role != UserRole.ADMIN and current_user.id != instructor.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this instructor",
        )

    instructor_data = instructor_update.dict(exclude_unset=True)
    for field, value in instructor_data.items():
        setattr(instructor, field, value)

    session.add(instructor)
    session.commit()
    session.refresh(instructor)

    return instructor


@router.delete("/{instructor_id}")
async def delete_instructor(
    instructor_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete instructors",
        )

    instructor = session.exec(
        select(Instructor).where(Instructor.id == instructor_id)
    ).first()
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found"
        )

    session.delete(instructor)
    session.commit()

    return {"message": "Instructor deleted successfully"}


@router.get("/{instructor_id}/courses", response_model=List[CourseRead])
async def get_instructor_courses(
    instructor_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    instructor = session.exec(
        select(Instructor).where(Instructor.id == instructor_id)
    ).first()
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found"
        )

    courses = session.exec(
        select(Course).where(Course.instructor_id == instructor_id)
    ).all()

    return courses
