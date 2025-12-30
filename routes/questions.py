from fastapi import APIRouter, Depends
from database.database import get_questions_collection
from bson import ObjectId

router = APIRouter(
    tags=["Questions"]
)

@router.get("/questions")
async def get_questions(questions=Depends(get_questions_collection)):
    docs = await questions.find().sort("id", 1).to_list(1000)

    for q in docs:
        q["_id"] = str(q["_id"])

    return docs