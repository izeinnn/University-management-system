from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from app.models import (
    Student,
    StudentCreate,
    StudentRead,
    StudentUpdate,
    User,
    UserRole,
    Enrollment,
    EnrollmentRead,
)
from app.database import get_session
from app.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=StudentRead)
async def create_student(
    student_data: StudentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    # Check if user is admin or the user creating their own student profile
    if current_user.role != UserRole.ADMIN and current_user.id != student_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create student profile",
        )

    # Check if student_id already exists
    existing_student = session.exec(
        select(Student).where(Student.student_id == student_data.student_id)
    ).first()
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Student ID already exists"
        )

    # Check if user exists and has student role
    user = session.exec(select(User).where(User.id == student_data.user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have student role",
        )

    db_student = Student(**student_data.dict())
    session.add(db_student)
    session.commit()
    session.refresh(db_student)

    return db_student


@router.get("/", response_model=List[StudentRead])
async def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role not in [UserRole.ADMIN, UserRole.INSTRUCTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view all students",
        )

    students = session.exec(select(Student).offset(skip).limit(limit)).all()
    return students


@router.get("/{student_id}", response_model=StudentRead)
async def get_student(
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    student = session.exec(select(Student).where(Student.id == student_id)).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    # Check if user is admin, instructor, or the student themselves
    if (
        current_user.role not in [UserRole.ADMIN, UserRole.INSTRUCTOR]
        and current_user.id != student.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this student",
        )

    return student


@router.put("/{student_id}", response_model=StudentRead)
async def update_student(
    student_id: int,
    student_update: StudentUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    student = session.exec(select(Student).where(Student.id == student_id)).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    # Check if user is admin or the student themselves
    if current_user.role != UserRole.ADMIN and current_user.id != student.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this student",
        )

    student_data = student_update.dict(exclude_unset=True)
    for field, value in student_data.items():
        setattr(student, field, value)

    session.add(student)
    session.commit()
    session.refresh(student)

    return student


@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete students",
        )

    student = session.exec(select(Student).where(Student.id == student_id)).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    session.delete(student)
    session.commit()

    return {"message": "Student deleted successfully"}


@router.get("/{student_id}/enrollments", response_model=List[EnrollmentRead])
async def get_student_enrollments(
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    student = session.exec(select(Student).where(Student.id == student_id)).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    # Check if user is admin, instructor, or the student themselves
    if (
        current_user.role not in [UserRole.ADMIN, UserRole.INSTRUCTOR]
        and current_user.id != student.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view student enrollments",
        )

    enrollments = session.exec(
        select(Enrollment).where(Enrollment.student_id == student_id)
    ).all()

    return enrollments
