from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"
    INSTRUCTOR = "instructor"


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class CourseStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"


class EnrollmentStatusEnum(str, Enum):
    ENROLLED = "enrolled"
    COMPLETED = "completed"
    DROPPED = "dropped"
    FAILED = "failed"


# Base User Model
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class UserCreate(UserBase):
    password: str


class UserUpdate(SQLModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    id: int
    created_at: datetime


# Student Model
class StudentBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    student_id: str = Field(unique=True, index=True)
    date_of_birth: Optional[datetime] = None
    gender: Optional[GenderEnum] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    enrollment_date: datetime = Field(default_factory=datetime.utcnow)


class Student(StudentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: Optional[User] = Relationship()
    enrollments: List["Enrollment"] = Relationship(back_populates="student")


class StudentCreate(StudentBase):
    pass


class StudentUpdate(SQLModel):
    date_of_birth: Optional[datetime] = None
    gender: Optional[GenderEnum] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None


class StudentRead(StudentBase):
    id: int
    user: Optional[UserRead] = None


# Instructor Model
class InstructorBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    employee_id: str = Field(unique=True, index=True)
    department: str
    hire_date: datetime = Field(default_factory=datetime.utcnow)
    salary: Optional[float] = None
    office_location: Optional[str] = None


class Instructor(InstructorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: Optional[User] = Relationship()
    courses: List["Course"] = Relationship(back_populates="instructor")


class InstructorCreate(InstructorBase):
    pass


class InstructorUpdate(SQLModel):
    department: Optional[str] = None
    salary: Optional[float] = None
    office_location: Optional[str] = None


class InstructorRead(InstructorBase):
    id: int
    user: Optional[UserRead] = None


# Course Model
class CourseBase(SQLModel):
    course_code: str = Field(unique=True, index=True)
    title: str
    description: Optional[str] = None
    credits: int
    instructor_id: int = Field(foreign_key="instructor.id")
    max_students: int = Field(default=30)
    status: CourseStatusEnum = Field(default=CourseStatusEnum.ACTIVE)


class Course(CourseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    instructor: Optional[Instructor] = Relationship(back_populates="courses")
    enrollments: List["Enrollment"] = Relationship(back_populates="course")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    credits: Optional[int] = None
    instructor_id: Optional[int] = None
    max_students: Optional[int] = None
    status: Optional[CourseStatusEnum] = None


class CourseRead(CourseBase):
    id: int
    instructor: Optional[InstructorRead] = None
    created_at: datetime
    enrolled_count: Optional[int] = None


# Enrollment Model
class EnrollmentBase(SQLModel):
    student_id: int = Field(foreign_key="student.id")
    course_id: int = Field(foreign_key="course.id")
    enrollment_date: datetime = Field(default_factory=datetime.utcnow)
    status: EnrollmentStatusEnum = Field(default=EnrollmentStatusEnum.ENROLLED)
    grade: Optional[str] = None


class Enrollment(EnrollmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student: Optional[Student] = Relationship(back_populates="enrollments")
    course: Optional[Course] = Relationship(back_populates="enrollments")


class EnrollmentCreate(SQLModel):
    student_id: int
    course_id: int


class EnrollmentUpdate(SQLModel):
    status: Optional[EnrollmentStatusEnum] = None
    grade: Optional[str] = None


class EnrollmentRead(EnrollmentBase):
    id: int
    student: Optional[StudentRead] = None
    course: Optional[CourseRead] = None


# Token Models
class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    email: Optional[str] = None
