from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
class Question(BaseModel):
    id: int
    category_id: int
    category_name: str
    question_text: str
    options: List[dict]

    class Config:
        json_encoders = {ObjectId: str}

class AssessmentResult(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user: str  
    score: int
    total_questions: int
    max_possible_score: int
    percentage: float
    risk_level: str
    answers: List[dict]

    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }