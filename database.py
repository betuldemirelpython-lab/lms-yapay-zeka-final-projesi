# database.py
"""SQLite database connection and basic CRUD helpers for the LMS.
Uses SQLAlchemy ORM with a SQLite file defined by DATABASE_URL in .env.
"""

import os
from pathlib import Path
from typing import List, Optional

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from dotenv import load_dotenv

# Load .env (project root)
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lms.db")

# Engine and session factory
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ----- ORM Models -----
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)  # In production use proper hashing
    # Relationships
    courses = relationship("Course", back_populates="owner")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="courses")
    lessons = relationship("Lesson", back_populates="course")

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    course = relationship("Course", back_populates="lessons")
    submissions = relationship("StudentSubmission", back_populates="lesson")

class StudentSubmission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    lesson = relationship("Lesson", back_populates="submissions")

# ----- Utility Functions -----
def get_db() -> Session:
    """Create a new DB session. Caller must close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Create tables if they do not exist."""
    Base.metadata.create_all(bind=engine)

# Example CRUD helpers (can be expanded later)
def create_user(db: Session, username: str, password_hash: str) -> User:
    user = User(username=username, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def create_course(db: Session, title: str, description: str, owner_id: int) -> Course:
    course = Course(title=title, description=description, owner_id=owner_id)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

def list_courses(db: Session) -> List[Course]:
    return db.query(Course).all()

def create_lesson(db: Session, title: str, content: str, course_id: int) -> Lesson:
    lesson = Lesson(title=title, content=content, course_id=course_id)
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson

def create_submission(db: Session, student_name: str, text: str, lesson_id: int) -> StudentSubmission:
    sub = StudentSubmission(student_name=student_name, text=text, lesson_id=lesson_id)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub
