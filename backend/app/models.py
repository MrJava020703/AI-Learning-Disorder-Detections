from datetime import datetime
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default="parent")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    students: Mapped[list["Student"]] = relationship(back_populates="owner")

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(30), default="Prefer not to say")
    grade: Mapped[str] = mapped_column(String(40))
    school: Mapped[str] = mapped_column(String(140), default="")
    language: Mapped[str] = mapped_column(String(20), default="English")
    guardian_name: Mapped[str] = mapped_column(String(120), default="")
    guardian_contact: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    owner: Mapped[User] = relationship(back_populates="students")
    assessments: Mapped[list["Assessment"]] = relationship(back_populates="student", cascade="all, delete-orphan")

class Assessment(Base):
    __tablename__ = "assessments"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="completed")
    questionnaire: Mapped[dict] = mapped_column(JSON, default=dict)
    reading_text: Mapped[str] = mapped_column(Text, default="")
    writing_text: Mapped[str] = mapped_column(Text, default="")
    dyslexia_score: Mapped[float] = mapped_column(Float)
    dysgraphia_score: Mapped[float] = mapped_column(Float)
    overall_risk: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(20))
    indicators: Mapped[list] = mapped_column(JSON, default=list)
    nlp_result: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    student: Mapped[Student] = relationship(back_populates="assessments")

class HandwritingSample(Base):
    __tablename__ = "handwriting_samples"
    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    ocr_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
