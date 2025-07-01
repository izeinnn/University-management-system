from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func
from typing import List
from app.models import (
    Enrollment,
    EnrollmentCreate,
    EnrollmentRead,
    EnrollmentUpdate,
    User,
    UserRole,
    Student,
    Course,
    Instructor,
    EnrollmentStatusEnum,
)
from app.database import get_session
from app.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=EnrollmentRead)
async def create_enrollment(
    enrollment_data: EnrollmentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    # Check if student exists
    student = session.exec(
        select(Student).where(Student.id == enrollment_data.student_id)
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    # Check if course exists
    course = session.exec(
        select(Course).where(Course.id == enrollment_data.course_id)
    ).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Check authorization - admin, student themselves, or course instructor
    instructor = session.exec(
        select(Instructor).where(Instructor.id == course.instructor_id)
    ).first()

    if (
        current_user.role != UserRole.ADMIN
        and current_user.id != student.user_id
        and (not instructor or current_user.id != instructor.user_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create enrollment",
        )

    # Check if student is already enrolled in this course
    existing_enrollment = session.exec(
        select(Enrollment).where(
            Enrollment.student_id == enrollment_data.student_id,
            Enrollment.course_id == enrollment_data.course_id,
            Enrollment.status == EnrollmentStatusEnum.ENROLLED,
        )
    ).first()
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is already enrolled in this course",
        )

    # Check if course has available spots
    enrolled_count = session.exec(
        select(func.count(Enrollment.id)).where(
            Enrollment.course_id == enrollment_data.course_id,
            Enrollment.status == EnrollmentStatusEnum.ENROLLED,
        )
    ).one()

    if enrolled_count >= course.max_students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Course is full"
        )

    db_enrollment = Enrollment(**enrollment_data.dict())
    session.add(db_enrollment)
    session.commit()
    session.refresh(db_enrollment)

    return db_enrollment


@router.get("/", response_model=List[EnrollmentRead])
async def get_enrollments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    student_id: int = Query(None),
    course_id: int = Query(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    query = select(Enrollment)

    if student_id:
        query = query.where(Enrollment.student_id == student_id)
    if course_id:
        query = query.where(Enrollment.course_id == course_id)

    enrollments = session.exec(query.offset(skip).limit(limit)).all()

    # Filter based on user permissions
    filtered_enrollments = []
    for enrollment in enrollments:
        student = session.exec(
            select(Student).where(Student.id == enrollment.student_id)
        ).first()
        course = session.exec(
            select(Course).where(Course.id == enrollment.course_id)
        ).first()
        instructor = (
            session.exec(
                select(Instructor).where(Instructor.id == course.instructor_id)
            ).first()
            if course
            else None
        )

        # Check if user can see this enrollment
        if (
            current_user.role == UserRole.ADMIN
            or (student and current_user.id == student.user_id)
            or (instructor and current_user.id == instructor.user_id)
        ):
            filtered_enrollments.append(enrollment)

    return filtered_enrollments


@router.get("/{enrollment_id}", response_model=EnrollmentRead)
async def get_enrollment(
    enrollment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    enrollment = session.exec(
        select(Enrollment).where(Enrollment.id == enrollment_id)
    ).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )

    # Check authorization
    student = session.exec(
        select(Student).where(Student.id == enrollment.student_id)
    ).first()
    course = session.exec(
        select(Course).where(Course.id == enrollment.course_id)
    ).first()
    instructor = (
        session.exec(
            select(Instructor).where(Instructor.id == course.instructor_id)
        ).first()
        if course
        else None
    )

    if (
        current_user.role != UserRole.ADMIN
        and (not student or current_user.id != student.user_id)
        and (not instructor or current_user.id != instructor.user_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this enrollment",
        )

    return enrollment


@router.put("/{enrollment_id}", response_model=EnrollmentRead)
async def update_enrollment(
    enrollment_id: int,
    enrollment_update: EnrollmentUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    enrollment = session.exec(
        select(Enrollment).where(Enrollment.id == enrollment_id)
    ).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )

    # Check authorization - admin, student (for dropping), or instructor (for grading)
    student = session.exec(
        select(Student).where(Student.id == enrollment.student_id)
    ).first()
    course = session.exec(
        select(Course).where(Course.id == enrollment.course_id)
    ).first()
    instructor = (
        session.exec(
            select(Instructor).where(Instructor.id == course.instructor_id)
        ).first()
        if course
        else None
    )

    is_authorized = False
    if current_user.role == UserRole.ADMIN:
        is_authorized = True
    elif student and current_user.id == student.user_id:
        # Students can only drop courses
        if enrollment_update.status and enrollment_update.status not in [
            EnrollmentStatusEnum.DROPPED
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students can only drop courses",
            )
        is_authorized = True
    elif instructor and current_user.id == instructor.user_id:
        # Instructors can update grades and status
        is_authorized = True

    if not is_authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this enrollment",
        )

    enrollment_data = enrollment_update.dict(exclude_unset=True)
    for field, value in enrollment_data.items():
        setattr(enrollment, field, value)

    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)

    return enrollment


@router.delete("/{enrollment_id}")
async def delete_enrollment(
    enrollment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete enrollments",
        )

    enrollment = session.exec(
        select(Enrollment).where(Enrollment.id == enrollment_id)
    ).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )

    session.delete(enrollment)
    session.commit()

    return {"message": "Enrollment deleted successfully"}
