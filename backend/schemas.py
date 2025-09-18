from pydantic import BaseModel

class StudentCreate(BaseModel):
    student_id: str
    name: str

class TeacherCreate(BaseModel):
    teacher_id: str
    name: str

class ScheduleCreate(BaseModel):
    class_id: str
    subject: str
    teacher_id: str
    day: str
    start_time: str
    end_time: str
