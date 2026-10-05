from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class Register(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=8)
    role: Literal['parent','teacher','admin']='parent'
class Login(BaseModel):
    email: EmailStr
    password: str
class Token(BaseModel):
    access_token: str
    token_type: str='bearer'
    user: dict
class StudentIn(BaseModel):
    name: str = Field(min_length=2); age: int = Field(ge=4,le=22); gender: str='Prefer not to say'; grade: str; school: str=''; language: str='English'; guardian_name: str=''; guardian_contact: str=''
class AssessmentIn(BaseModel):
    student_id: int; questionnaire: dict={}; reading_text: str=''; writing_text: str=''
class OCRText(BaseModel): text: str
