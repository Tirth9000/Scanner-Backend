from fastapi import APIRouter, Depends
from database.database import (
    get_questions_collection,
    get_assessment_results_collection,
)
from services.auth import get_current_user
from models.Assesment import AssessmentResult

router = APIRouter(
    tags=["Asses"]
)

@router.post("/assess")
async def assess(payload: dict,
    user=Depends(get_current_user),
    questions=Depends(get_questions_collection),
    results=Depends(get_assessment_results_collection)
):
    answers = payload["answers"]
    user_id = str(user["_id"])
    score = 0
    answer_docs = []

    for ans in answers:
        q = await questions.find_one({"id": ans["questionId"]})
        opt = next(o for o in q["options"] if o["option_key"] == ans["selectedOption"])

        score += opt["score"]

        answer_docs.append({
            "questionId": ans["questionId"],
            "selectedOption": ans["selectedOption"],
            "pointsAwarded": opt["score"]
        })

    max_score = len(answers) * 3
    percentage = (score / max_score) * 100
    risk_level = "Critical" if percentage < 40 else "Moderate" if percentage < 70 else "Secure"

    result = AssessmentResult(
        user=user_id,
        score=score,
        total_questions=len(answers),
        max_possible_score=max_score,
        percentage=percentage,
        risk_level=risk_level,
        answers=answer_docs
    )

    await results.insert_one(result.to_dict())
    saved={
        "user": user_id,
        "score": score,
        "total_questions": len(answers),
        "max_possible_score": max_score,
        "percentage": percentage,
        "risk_level": risk_level,
        "answers": answer_docs
    }
    return saved