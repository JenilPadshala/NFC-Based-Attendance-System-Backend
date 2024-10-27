from datetime import date
from typing import List
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import engine, SessionLocal
from pydantic import BaseModel
models.Base.metadata.create_all(bind=engine)
from fastapi.middleware.cors import CORSMiddleware

#init FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Welcome to the NFC-Based Attendance System"}


# Faculty login route
@app.post("/faculty/login", response_model=schemas.FacultyResponse)
def faculty_login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    faculty = crud.get_faculty_by_username(db, username=user.username, password = user.password)
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return schemas.FacultyResponse(
        faculty_id=faculty.faculty_id,
        first_name=faculty.first_name,
        last_name=faculty.last_name,
        email=faculty.email,
        department=faculty.department,
    )

# Student login route
@app.post("/student/login", response_model=schemas.StudentResponse)
def student_login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    student = crud.get_student_by_username(db, username=user.username, password = user.password)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return schemas.StudentResponse(
        student_id=student.student_id,
        first_name=student.first_name,
        last_name=student.last_name,
        email=student.email,
        nfc_tag_id=student.nfc_tag_id,
    )


# Get student attendance route
@app.get("/student/{student_id}/attendance", response_model=List[schemas.CourseAttendanceResponse])
def get_student_attendance(student_id: int, db: Session = Depends(get_db)):
    attendance_data = crud.get_attendance_percentage_by_student(db, student_id)
    if not attendance_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No attendance data found for the student",
        )
    return attendance_data

# Get faculty courses route
@app.get("/faculty/{faculty_id}/courses", response_model=List[schemas.CourseResponse])
def get_courses_for_faculty(faculty_id: int, db: Session = Depends(get_db)):
    
    courses = crud.get_courses_by_faculty(db, faculty_id = faculty_id)

    if not courses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No courses found for the faculty",
        )
    return courses


# Accept NFC Tag route
@app.post("/faculty/{faculty_id}/{course_id}/attendance", response_model=schemas.AttendanceResponse)
def take_attendance(course_id: int, faculty_id: int, attendance_data: schemas.AttendanceRequest, db: Session = Depends(get_db)):
    
    #Check if the faculty is teaching the course
    course = db.query(models.Course).filter(models.Course.course_id == course_id, models.Course.faculty_id == faculty_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Course not found for the faculty",
        )
    
    #Get the student by NFC tag
    student = db.query(models.Student).filter(models.Student.nfc_tag_id == attendance_data.nfc_tag_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Student not found",
        )
    
    #Check if the student is enrolled in the course
    if not crud.is_student_enrolled(db, student_id = student.student_id, course_id = course_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Student is not enrolled in the course",
        )
    
    #Check if attendance has already been marked for today
    if crud.has_attendance_for_today(db, student_id = student.student_id, course_id = course_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Attendance already marked for today",
        )
    
    # Add the attendance record
    crud.add_attendance(db, student_id = student.student_id, course_id = course_id)

    return schemas.AttendanceResponse(message="Attendance marked successfully")

# Finalize attendance route
@app.post("/faculty/{faculty_id}/{course_id}/finalize-attendance")
def finalize_attenance(course_id: int, faculty_id: int, db: Session = Depends(get_db)):
    """
    Finalize attendance for the course by marking absent the students who didn't provide their nfc_tag_id.
    After marking, redirect the faculty to the course list.
    """
    #Ensure the faculty is teaching the course
    course = db.query(models.Course).filter(models.Course.course_id == course_id, models.Course.faculty_id == faculty_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Course not found for the faculty"
        )
    
    #get present student ids
    present_student_ids = crud.get_present_students(db, course_id = course_id, date = date.today())

    crud.mark_absent_students(db, course_id = course_id, present_student_ids = present_student_ids)

    # Redirect the faculty to the course list
    # return RedirectResponse(url = f"/faculty/{faculty_id}/courses", status_code=status.HTTP_303_SEE_OTHER)
    return schemas.FinalAttendanceResponse(redirect_url = f"/faculty/{faculty_id}/courses")
