from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum

# Enum for roles
class UserRole(enum.Enum):
    student = "student"
    faculty = "faculty"

# Enum for attendance status
class AttendanceStatus(enum.Enum):
    present = "Present"
    absent = "Absent"

# 1. User Table
class User(Base):
    __tablename__ = "Users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # Store hashed passwords
    role = Column(Enum(UserRole), nullable=False)  # Enum for role-based access

    # Relationship with Student and Faculty (established in Student and Faculty models)
    student = relationship("Student", back_populates="user")
    faculty = relationship("Faculty", back_populates="user")


# 2. Faculty Table
class Faculty(Base):
    __tablename__ = "Faculty"

    faculty_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    department = Column(String, nullable=False)
    
    # Foreign key relationship
    courses = relationship("Course", back_populates="faculty")  # A faculty can teach many courses

    # Relationship with User Table
    user_id = Column(Integer, ForeignKey("Users.user_id"))
    user = relationship("User", back_populates="faculty")


# 3. Student Table
class Student(Base):
    __tablename__ = "Students"

    student_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    nfc_tag_id = Column(String, unique=True, nullable=False)  # Unique NFC tag for each student

    # Relationship with Enrollments and Attendance
    enrollments = relationship("Enrollment", back_populates="student")  # A student can have many enrollments
    attendance = relationship("Attendance", back_populates="student")  # A student can have many attendance records

    # Relationship with User Table
    user_id = Column(Integer, ForeignKey("Users.user_id"))
    user = relationship("User", back_populates="student")


# 4. Course Table
class Course(Base):
    __tablename__ = "Courses"

    course_id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False)
    # Foreign key to Faculty Table
    faculty_id = Column(Integer, ForeignKey("Faculty.faculty_id"), nullable=False)
    start_date = Column(Date, nullable=False)
    # Relationship with Faculty and Enrollments
    faculty = relationship("Faculty", back_populates="courses")  # Each course has one faculty member
    enrollments = relationship("Enrollment", back_populates="course")  # A course can have many enrollments
    attendance = relationship("Attendance", back_populates="course")  # A course can have many attendance records


# 5. Enrollment Table
class Enrollment(Base):
    __tablename__ = "Enrollment"

    enrollment_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys to Course and Student Tables
    course_id = Column(Integer, ForeignKey("Courses.course_id"), nullable=False)
    student_id = Column(Integer, ForeignKey("Students.student_id"), nullable=False)

    # Relationships
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


# 6. Attendance Table
class Attendance(Base):
    __tablename__ = "Attendance"

    attendance_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys to Student and Course Tables
    student_id = Column(Integer, ForeignKey("Students.student_id"), nullable=False)
    course_id = Column(Integer, ForeignKey("Courses.course_id"), nullable=False)

    attendance_date = Column(Date, nullable=False)  # Date of the attendance record
    status = Column(Enum(AttendanceStatus), nullable=False)  # Present/Absent status

    # Relationships
    student = relationship("Student", back_populates="attendance")
    course = relationship("Course", back_populates="attendance")
