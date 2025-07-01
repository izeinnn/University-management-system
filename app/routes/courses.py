from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func
from typing import List
from app.models import (
    Course,
    CourseCreate,
    CourseRead,
    CourseUpdate,
    User,
    UserRole,
    Enrollment,
    EnrollmentRead,
    Instructor,
)
from app.database import get_session
from app.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=CourseRead)
async def create_course(
    course_data: CourseCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    # Only admins can create courses
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create courses",
        )

    # Check if course_code already exists
    existing_course = session.exec(
        select(Course).where(Course.course_code == course_data.course_code)
    ).first()
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Course code already exists"
        )

    # Check if instructor exists
    instructor = session.exec(
        select(Instructor).where(Instructor.id == course_data.instructor_id)
    ).first()
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found"
        )

    db_course = Course(**course_data.dict())
    session.add(db_course)
    session.commit()
    session.refresh(db_course)

    return db_course


@router.get("/", response_model=List[CourseRead])
async def get_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    courses = session.exec(select(Course).offset(skip).limit(limit)).all()

    # Add enrolled count for each course
    for course in courses:
        enrolled_count = session.exec(
            select(func.count(Enrollment.id)).where(
                Enrollment.course_id == course.id, Enrollment.status == "enrolled"
            )
        ).one()
        course.enrolled_count = enrolled_count

    return courses


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(
    course_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    course = session.exec(select(Course).where(Course.id == course_id)).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Add enrolled count
    enrolled_count = session.exec(
        select(func.count(Enrollment.id)).where(
            Enrollment.course_id == course.id, Enrollment.status == "enrolled"
        )
    ).one()
    course.enrolled_count = enrolled_count

    return course


@router.put("/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    course = session.exec(select(Course).where(Course.id == course_id)).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Check if user is admin or the course instructor
    instructor = session.exec(
        select(Instructor).where(Instructor.id == course.instructor_id)
    ).first()

    if current_user.role != UserRole.ADMIN and (
        not instructor or current_user.id != instructor.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this course",
        )

    course_data = course_update.dict(exclude_unset=True)
    for field, value in course_data.items():
        setattr(course, field, value)

    session.add(course)
    session.commit()
    session.refresh(course)

    return course


@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete courses",
        )

    course = session.exec(select(Course).where(Course.id == course_id)).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    session.delete(course)
    session.commit()

    return {"message": "Course deleted successfully"}


@router.get("/{course_id}/enrollments", response_model=List[EnrollmentRead])
async def get_course_enrollments(
    course_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    course = session.exec(select(Course).where(Course.id == course_id)).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Check if user is admin or the course instructor
    instructor = session.exec(
        select(Instructor).where(Instructor.id == course.instructor_id)
    ).first()

    if current_user.role != UserRole.ADMIN and (
        not instructor or current_user.id != instructor.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view course enrollments",
        )

    enrollments = session.exec(
        select(Enrollment).where(Enrollment.course_id == course_id)
    ).all()

    return enrollments
