from sqlmodel import SQLModel, create_engine, Session
from app.models import *
from app.auth import get_password_hash
from datetime import datetime, date
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///university.db")
engine = create_engine(DATABASE_URL, echo=True)


def create_sample_data():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Create admin user
        admin_user = User(
            email="admin@university.edu",
            first_name="Admin",
            last_name="User",
            phone="+1234567890",
            role=UserRole.ADMIN,
            hashed_password=get_password_hash("admin123"),
        )
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)

        # Create instructor users
        instructor1_user = User(
            email="john.smith@university.edu",
            first_name="John",
            last_name="Smith",
            phone="+1234567891",
            role=UserRole.INSTRUCTOR,
            hashed_password=get_password_hash("instructor123"),
        )
        session.add(instructor1_user)

        instructor2_user = User(
            email="jane.doe@university.edu",
            first_name="Jane",
            last_name="Doe",
            phone="+1234567892",
            role=UserRole.INSTRUCTOR,
            hashed_password=get_password_hash("instructor123"),
        )
        session.add(instructor2_user)
        session.commit()
        session.refresh(instructor1_user)
        session.refresh(instructor2_user)

        # Create instructors
        instructor1 = Instructor(
            user_id=instructor1_user.id,
            employee_id="EMP001",
            department="Computer Science",
            salary=75000.00,
            office_location="CS Building Room 101",
        )
        session.add(instructor1)

        instructor2 = Instructor(
            user_id=instructor2_user.id,
            employee_id="EMP002",
            department="Mathematics",
            salary=70000.00,
            office_location="Math Building Room 201",
        )
        session.add(instructor2)
        session.commit()
        session.refresh(instructor1)
        session.refresh(instructor2)

        # Create student users
        student1_user = User(
            email="alice.johnson@student.university.edu",
            first_name="Alice",
            last_name="Johnson",
            phone="+1234567893",
            role=UserRole.STUDENT,
            hashed_password=get_password_hash("student123"),
        )
        session.add(student1_user)

        student2_user = User(
            email="bob.wilson@student.university.edu",
            first_name="Bob",
            last_name="Wilson",
            phone="+1234567894",
            role=UserRole.STUDENT,
            hashed_password=get_password_hash("student123"),
        )
        session.add(student2_user)

        student3_user = User(
            email="carol.brown@student.university.edu",
            first_name="Carol",
            last_name="Brown",
            phone="+1234567895",
            role=UserRole.STUDENT,
            hashed_password=get_password_hash("student123"),
        )
        session.add(student3_user)
        session.commit()
        session.refresh(student1_user)
        session.refresh(student2_user)
        session.refresh(student3_user)

        # Create students
        student1 = Student(
            user_id=student1_user.id,
            student_id="STU001",
            date_of_birth=datetime(2000, 5, 15),
            gender=GenderEnum.FEMALE,
            address="123 University Ave, College Town",
            emergency_contact="+1234567896",
        )
        session.add(student1)

        student2 = Student(
            user_id=student2_user.id,
            student_id="STU002",
            date_of_birth=datetime(1999, 8, 22),
            gender=GenderEnum.MALE,
            address="456 Campus Dr, College Town",
            emergency_contact="+1234567897",
        )
        session.add(student2)

        student3 = Student(
            user_id=student3_user.id,
            student_id="STU003",
            date_of_birth=datetime(2001, 2, 10),
            gender=GenderEnum.FEMALE,
            address="789 Student St, College Town",
            emergency_contact="+1234567898",
        )
        session.add(student3)
        session.commit()
        session.refresh(student1)
        session.refresh(student2)
        session.refresh(student3)

        # Create courses
        course1 = Course(
            course_code="CS101",
            title="Introduction to Programming",
            description="Learn the fundamentals of programming using Python",
            credits=3,
            instructor_id=instructor1.id,
            max_students=25,
            status=CourseStatusEnum.ACTIVE,
        )
        session.add(course1)

        course2 = Course(
            course_code="CS201",
            title="Data Structures and Algorithms",
            description="Advanced programming concepts and algorithm design",
            credits=4,
            instructor_id=instructor1.id,
            max_students=20,
            status=CourseStatusEnum.ACTIVE,
        )
        session.add(course2)

        course3 = Course(
            course_code="MATH101",
            title="Calculus I",
            description="Introduction to differential calculus",
            credits=4,
            instructor_id=instructor2.id,
            max_students=30,
            status=CourseStatusEnum.ACTIVE,
        )
        session.add(course3)

        course4 = Course(
            course_code="MATH201",
            title="Linear Algebra",
            description="Matrices, vector spaces, and linear transformations",
            credits=3,
            instructor_id=instructor2.id,
            max_students=25,
            status=CourseStatusEnum.ACTIVE,
        )
        session.add(course4)
        session.commit()
        session.refresh(course1)
        session.refresh(course2)
        session.refresh(course3)
        session.refresh(course4)

        # Create enrollments
        enrollment1 = Enrollment(
            student_id=student1.id,
            course_id=course1.id,
            status=EnrollmentStatusEnum.ENROLLED,
        )
        session.add(enrollment1)

        enrollment2 = Enrollment(
            student_id=student1.id,
            course_id=course3.id,
            status=EnrollmentStatusEnum.ENROLLED,
        )
        session.add(enrollment2)

        enrollment3 = Enrollment(
            student_id=student2.id,
            course_id=course1.id,
            status=EnrollmentStatusEnum.ENROLLED,
        )
        session.add(enrollment3)

        enrollment4 = Enrollment(
            student_id=student2.id,
            course_id=course2.id,
            status=EnrollmentStatusEnum.ENROLLED,
        )
        session.add(enrollment4)

        enrollment5 = Enrollment(
            student_id=student3.id,
            course_id=course3.id,
            status=EnrollmentStatusEnum.ENROLLED,
        )
        session.add(enrollment5)

        enrollment6 = Enrollment(
            student_id=student3.id,
            course_id=course4.id,
            status=EnrollmentStatusEnum.ENROLLED,
        )
        session.add(enrollment6)

        session.commit()

        print("Sample data created successfully!")
        print("\nSample login credentials:")
        print("Admin: admin@university.edu / admin123")
        print("Instructor 1: john.smith@university.edu / instructor123")
        print("Instructor 2: jane.doe@university.edu / instructor123")
        print("Student 1: alice.johnson@student.university.edu / student123")
        print("Student 2: bob.wilson@student.university.edu / student123")
        print("Student 3: carol.brown@student.university.edu / student123")


if __name__ == "__main__":
    create_sample_data()
