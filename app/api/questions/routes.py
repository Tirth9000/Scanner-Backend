from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from db.base import getCursor
import json


router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("/")
async def get_questions():
    try:
        cursor = getCursor()
        cursor.execute(
            """
            SELECT _id, category_id, category_name, question_text, options
            FROM questions
            ORDER BY _id ASC
            """
        )
        rows = cursor.fetchall() or []
        cursor.close()

        questions = []
        for q_id, category_id, category_name, question_text, options in rows:
            if isinstance(options, str):
                try:
                    options = json.loads(options)
                except Exception:
                    pass
            questions.append(
                {
                    "_id": q_id,
                    "category_id": category_id,
                    "category_name": category_name,
                    "question_text": question_text,
                    "options": options,
                }
            )

        return JSONResponse(status_code=200, content=questions)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to fetch questions")

