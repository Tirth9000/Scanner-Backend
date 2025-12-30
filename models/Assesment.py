from datetime import datetime
from typing import List
from bson import ObjectId

class Question:
    def __init__(self, id, category_id, category_name, question_text, options):
        self.id = id
        self.category_id = category_id
        self.category_name = category_name
        self.question_text = question_text
        self.options = options

    def to_dict(self):
        return self.__dict__

class AssessmentResult:
    def __init__(
        self,
        user,
        score,
        total_questions,
        max_possible_score,
        percentage,
        risk_level,
        answers,
        _id=None,
        createdAt=None,
        updatedAt=None,
    ):
        self._id = _id or ObjectId()
        self.user = user
        self.score = score
        self.total_questions = total_questions
        self.max_possible_score = max_possible_score
        self.percentage = percentage
        self.risk_level = risk_level
        self.answers = answers
        self.createdAt = createdAt or datetime.utcnow()
        self.updatedAt = updatedAt or datetime.utcnow()

    def to_dict(self):
        return self.__dict__