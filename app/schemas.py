from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from enum import Enum


# Enum for User Roles
class UserRole(str, Enum):
    student = "student"
    faculty = "faculty"

# Enum for Attendance Status
class AttendanceStatus(str, Enum):
    present = "present"
    absent = "absent"

# 1. User Login Pydantic Model
class UserLogin(BaseModel):
    username: str
    password: str
    
# 2. Faculty Login Pydantic Model
class FacultyResponse(BaseModel):
    faculty_id: int
    first_name: str
    last_name: str
    email: str
    department: str

# 3. Student Login Pydantic Model
class StudentResponse(BaseModel):
    student_id: int
    first_name: str
    last_name: str
    email: str
    nfc_tag_id: str

# 4. Student Attendance Pydantic Model
class CourseAttendanceResponse(BaseModel):
    course_name: str
    attendance_percentage : float
    class Config:
        orm_mode = True

# 5. Faculty Course Pydantic Model
class CourseResponse(BaseModel):
    course_id: int
    course_name: str

    class Config:
        orm_mode = True

# 6. Accept NFC Tag Pydantic Model
class AttendanceRequest(BaseModel):
    nfc_tag_id : str

class AttendanceResponse(BaseModel):
    message: str
