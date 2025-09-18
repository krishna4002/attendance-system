from sqlalchemy import Column, Integer, String
from database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

class AttendanceStudent(Base):
    __tablename__ = "attendance_students"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True, nullable=False)
    date = Column(String)
    time = Column(String)
    status = Column(String)

class AttendanceTeacher(Base):
    __tablename__ = "attendance_teachers"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, index=True, nullable=False)
    date = Column(String)
    time = Column(String)
    status = Column(String)

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(String)
    subject = Column(String)
    teacher_id = Column(String)
    day = Column(String)
    start_time = Column(String)
    end_time = Column(String)

class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, index=True)
    password_hash = Column(String)
