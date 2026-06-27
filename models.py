# models.py
"""Pydantic models (schemas) for the LMS FastAPI service.
These are used for request validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# ----- User schemas -----
class UserCreate(BaseModel):
    username: str = Field(..., example="student1")
    password: str = Field(..., example="securepassword")

class UserRead(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

# ----- Course schemas -----
class CourseCreate(BaseModel):
    title: str = Field(..., example="Python Programlama")
    description: Optional[str] = Field(None, example="Temel Python programlama kursu.")
    owner_id: int = Field(..., example=1)

class CourseRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    owner_id: int

    class Config:
        orm_mode = True

# ----- Lesson schemas -----
class LessonCreate(BaseModel):
    title: str = Field(..., example="Giriş ve Değişkenler")
    content: Optional[str] = Field(None, example="Bu derste Python değişkenleri ele alınır.")
    course_id: int = Field(..., example=1)

class LessonRead(BaseModel):
    id: int
    title: str
    content: Optional[str]
    course_id: int

    class Config:
        orm_mode = True

# ----- Student submission schemas -----
class SubmissionCreate(BaseModel):
    student_name: str = Field(..., example="Ali Veli")
    text: str = Field(..., example="Ödev metni burada.")
    lesson_id: int = Field(..., example=1)

class SubmissionRead(BaseModel):
    id: int
    student_name: str
    text: str
    lesson_id: int

    class Config:
        orm_mode = True
