from datetime import datetime
from typing import List
from bson import ObjectId

class User:
    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        _id=None,
        createdAt=None,
        updatedAt=None,
    ):
        self._id = _id or ObjectId()
        self.username = username
        self.email = email
        self.password = password
        self.createdAt = createdAt or datetime.utcnow()
        self.updatedAt = updatedAt or datetime.utcnow()

    def to_dict(self):
        return self.__dict__