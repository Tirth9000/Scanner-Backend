from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from db.base import getCursor
import os
import json


router = APIRouter(prefix="/api/seed", tags=["insert_questions"])


def seed_questions_data():
    try:
        cursor = getCursor()

        # Check if questions already exist
        cursor.execute("SELECT COUNT(*) FROM questions")
        row = cursor.fetchone()
        count = row[0] if row is not None else 0

        if count > 0:
            cursor.close()
            return (False, "Questions already exist — seeding skipped", count)

        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        data_path = os.path.join(app_dir, "data", "questionsData.json")

        with open(data_path, "r", encoding="utf-8") as f:
            questions = json.load(f)

        # Insert questions into DB
        # NOTE: questions table now uses `_id` as the primary key column,
        # but the JSON still has `id`. We store that value into `_id`.
        insert_sql = """
            INSERT INTO questions (_id, category_id, category_name, question_text, options)
            VALUES (%s, %s, %s, %s, %s)
        """

        for q in questions:
            cursor.execute(
                insert_sql,
                (
                    q["id"],
                    q["category_id"],
                    q["category_name"],
                    q["question_text"],
                    json.dumps(q["options"]),
                ),
            )

        cursor.close()
        return (True, "Questions seeded successfully", len(questions))

    except Exception as e:
        print(f"Error seeding questions: {e}")
        raise


@router.post("/")
async def seed_questions():
    try:
        success, message, count = seed_questions_data()
        
        status_code = 201 if success else 200
        return JSONResponse(
            status_code=status_code,
            content={
                "message": message,
                "count": count,
            },
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Server Error")

