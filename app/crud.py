from datetime import date
from typing import List
from sqlalchemy.orm import Session
from .models import Attendance, AttendanceStatus, Course, Faculty, User, Student, Enrollment



def get_faculty_by_username(db: Session, username: str, password: str) -> Faculty:
    """
    Get faculty by username
    """
    # first check if the user exists
    user = db.query(User).filter(User.username == username).one_or_none()
    if not user:
        return None
    # if user exists, check if the user is a faculty
    faculty = db.query(Faculty).filter(Faculty.user_id == user.user_id).one_or_none()
    if faculty and user.password == password:
        return faculty



def get_student_by_username(db: Session, username: str, password: str) -> Student:
    """
    Get student by username
    """
    # first check if the user exists
    user = db.query(User).filter(User.username == username).one_or_none()
    if not user:
        return None
    # if user exists, check if the user is a student
    student = db.query(Student).filter(Student.user_id == user.user_id).one_or_none()
    if student and user.password == password:
        return student
    



def get_attendance_percentage_by_student(db: Session, student_id: int) -> float:
    """
    Get attendance percentage for each course a student is enrolled in.
    """

    #Get all courses the student is enrolled in 
    courses = (
        db.query(Course)
        .join(Enrollment)
        .filter(Enrollment.student_id == student_id)
        .all()
    )

    course_attendance = []

    #loop through each course and calculate attendance percentage
    for course in courses:
        total_classes = (
            db.query(Attendance)
            .filter(
                Attendance.course_id == course.course_id,
                Attendance.student_id == student_id,
                Attendance.attendance_date >= course.start_date
                )
            .count())
        
        attended_classes = (
            db.query(Attendance)
            .filter(
                Attendance.course_id == course.course_id, 
                Attendance.student_id == student_id, 
                Attendance.status == 'present')
            .count()
        )
        attendance_percentage = (attended_classes / total_classes) * 100 if total_classes > 0 else 0

        course_attendance.append(
            {
                "course_name": course.course_name,
                "attendance_percentage": attendance_percentage,
            }
        )
    return course_attendance




def get_courses_by_faculty(db: Session, faculty_id: int) -> List[Course]:
    """
    Get courses by faculty
    """
    return db.query(Course).filter(Course.faculty_id == faculty_id).all()



def is_student_enrolled(db: Session, student_id: int, course_id: int):
    """
    Check if a student is enrolled in a course
    """
    return db.query(Enrollment).filter(
        Enrollment.student_id == student_id, 
        Enrollment.course_id == course_id
    ).first()



def has_attendance_for_today(db: Session, student_id: int, course_id: int):
    """
    Check if a student has attendance for today
    """
    today = date.today()
    return db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.course_id == course_id,
        Attendance.attendance_date == today
    ).first()

def add_attendance(db: Session, student_id: int, course_id: int):
    """
    Add attendance for a student
    """
    new_attendance = Attendance(
        student_id = student_id, 
        course_id = course_id,
        attendance_date = date.today(),
        status = AttendanceStatus.present
    )
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    return new_attendance


# mark absent for students not present
def mark_absent_students(db: Session, course_id: int, present_student_ids: list[int]):
    """ Mark students absent if they were not marked present. """
    # Get all students enrolled in the course
    enrolled_students = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()

    today = date.today()
    for enrollment in enrolled_students:
        student_id = enrollment.student_id

        # If the student is not in the list of present stduents, mark them absent
        if student_id not in present_student_ids:
            #Check if they already have an attendance record for today
            attendance_exists = db.query(Attendance).filter(
                Attendance.student_id == student_id,
                Attendance.course_id == course_id,
                Attendance.attendance_date == today
            ).first()

            if not attendance_exists:
                new_attendance = Attendance(
                    student_id = student_id, 
                    course_id = course_id,
                    attendance_date = today,
                    status = AttendanceStatus.absent
                )
                db.add(new_attendance)
    db.commit()

# Get all the students marked as present for a course on given date and return a list of their student ids
def get_present_students(db: Session, course_id: int, date: date):
    """ Get all the students marked as present for a course on given date and return a list of their student ids. """
    present_students = db.query(Attendance.student_id).filter(
        Attendance.course_id == course_id,
        Attendance.attendance_date == date,
        Attendance.status == AttendanceStatus.present
    ).all()
    return [student_id for student_id, in present_students]