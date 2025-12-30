from pydantic import BaseModel, EmailStr
from typing import List, Optional

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    username: str

class SigninRequest(BaseModel):
    email: EmailStr
    password: str

class QuestionOptionSchema(BaseModel):
    option_key: str
    option_text: str
    score: int

class QuestionResponseSchema(BaseModel):
    _id: str
    id: int
    category_id: int
    category_name: str
    question_text: str
    options: List[QuestionOptionSchema]