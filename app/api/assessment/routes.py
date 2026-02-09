from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import Response
import json
from api.assessment.schemas import SubmitAssessmentBody
from core.middleware import protect
from db.base import getCursor
from utils.generate_assessment_pdf import generate_assessment_pdf_bytes


router = APIRouter(prefix="/api/assess", tags=["assessment"])


def calculateGrade(percentage: int) -> str:
    if percentage >= 90:
        return "A"
    if percentage >= 80:
        return "B"
    if percentage >= 70:
        return "C"
    if percentage >= 60:
        return "D"
    return "F"


def mapGradeToRisk(grade: str) -> str:
    if grade == "A":
        return "Secure"
    if grade == "B":
        return "Low"
    if grade == "C":
        return "Medium"
    if grade == "D":
        return "High"
    if grade == "F":
        return "Critical"
    return "Unknown"


def mapRiskToColor(risk: str) -> str:
    if risk in ("Secure", "Low"):
        return "green"
    if risk == "Medium":
        return "yellow"
    if risk in ("High", "Critical"):
        return "red"
    return "gray"


@router.post("/")
async def submit_assessment(body: SubmitAssessmentBody, user: dict = Depends(protect)):
    try:
        answers = body.answers
        if not isinstance(answers, list) or len(answers) == 0:
            return JSONResponse(status_code=400, content={"error": "Invalid answers payload"})

        cursor = getCursor()
        cursor.execute("SELECT _id, category_name, question_text, options FROM questions")
        rows = cursor.fetchall() or []

        if len(rows) == 0:
            cursor.close()
            return JSONResponse(status_code=500, content={"error": "No questions found"})

        # Map: question _id (int) -> {category_name, question_text, options(list)}
        questionMap = {}
        for q_id, category_name, question_text, options in rows:
            # psycopg may give dict/list for JSONB; if it's a string, decode it
            if isinstance(options, str):
                try:
                    options = json.loads(options)
                except Exception:
                    options = []
            questionMap[str(q_id)] = {
                "_id": q_id,
                "category_name": category_name,
                "question_text": question_text,
                "options": options or [],
            }

        totalScore = 0
        maxPossibleScore = 0
        categoryTracker = {}
        processedAnswers = []

        # max score bookkeeping (same as JS: each question max = 3)
        for _, category_name, _, _ in rows:
            if category_name not in categoryTracker:
                categoryTracker[category_name] = {"score": 0, "max": 0}
            categoryTracker[category_name]["max"] += 3
            maxPossibleScore += 3

        for ans in answers:
            qid = ans.questionId
            # Our Postgres questions now use numeric _id as primary key.
            if not isinstance(qid, str) or not qid.isdigit():
                cursor.close()
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Invalid questionId payload (expected numeric question id). "
                        "Fetch questions from GET /api/questions and send their numeric id."
                    },
                )

            question = questionMap.get(qid)
            if not question:
                continue

            options = question["options"]
            idx = ans.selectedOption
            if idx < 0 or idx >= len(options):
                cursor.close()
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Invalid selectedOption {idx} for question {qid} (must be 0, 1, 2, or 3)"},
                )
            selectedOption = options[idx]

            if isinstance(selectedOption, dict):
                score_val = selectedOption.get("score")
                points = int(score_val) if score_val is not None else 0
            else:
                points = 0

            totalScore += points
            categoryTracker[question["category_name"]]["score"] += points

            processedAnswers.append(
                {
                    "questionId": question["_id"],
                    "questionText": question["question_text"],
                    "selectedOption": (
                        {
                            "option_key": selectedOption.get("option_key"),
                            "option_text": selectedOption.get("option_text"),
                            "score": selectedOption.get("score"),
                        }
                        if isinstance(selectedOption, dict)
                        else None
                    ),
                    "pointsAwarded": points,
                    "quotation": ans.quotation or None,
                }
            )

        # CATEGORY SCORES
        categoryScores = []
        for name, data in categoryTracker.items():
            percentage = round((data["score"] / data["max"]) * 100) if data["max"] > 0 else 0
            grade = calculateGrade(percentage)
            risk = mapGradeToRisk(grade)
            color = mapRiskToColor(risk)
            categoryScores.append(
                {
                    "category_name": name,
                    "score": data["score"],
                    "max_score": data["max"],
                    "percentage": percentage,
                    "grade": grade,
                    "risk": risk,
                    "color": color,
                }
            )

        # OVERALL SUMMARY
        overallPercentage = round((totalScore / maxPossibleScore) * 100) if maxPossibleScore > 0 else 0
        overallGrade = calculateGrade(overallPercentage)
        overallRisk = mapGradeToRisk(overallGrade)
        overallColor = mapRiskToColor(overallRisk)

        summary = {
            "score": totalScore,
            "total_questions": len(rows),
            "max_possible_score": maxPossibleScore,
            "percentage": overallPercentage,
            "grade": overallGrade,
            "risk_level": overallRisk,
            "risk_color": overallColor,
        }

        cursor.execute(
            """
            INSERT INTO assessment_results (_id, user_id, summary, category_scores, answers)
            VALUES (gen_random_uuid(), %s, %s, %s, %s)
            RETURNING _id, user_id, summary, category_scores, answers, created_at, updated_at
            """,
            (
                user["id"],
                json.dumps(summary),
                json.dumps(categoryScores),
                json.dumps(processedAnswers),
            ),
        )
        created = cursor.fetchone()
        cursor.close()

        if not created:
            return JSONResponse(status_code=500, content={"error": "Assessment submission failed"})

        result_id, user_id, db_summary, db_category_scores, db_answers, created_at, updated_at = created

        # Normalize jsonb outputs if needed
        def _maybe_load(v):
            if isinstance(v, str):
                try:
                    return json.loads(v)
                except Exception:
                    return v
            return v

        data = {
            "_id": str(result_id),
            "user": user_id,
            "summary": _maybe_load(db_summary),
            "category_scores": _maybe_load(db_category_scores),
            "answers": _maybe_load(db_answers),
            "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else created_at,
            "updated_at": updated_at.isoformat() if hasattr(updated_at, "isoformat") else updated_at,
        }

        return JSONResponse(status_code=200, content={"success": True, "resultId": str(result_id), "data": data})

    except Exception as err:
        print("ASSESSMENT SUBMIT ERROR:", err)
        return JSONResponse(status_code=500, content={"error": "Assessment submission failed"})


@router.get("/history")
async def history(user: dict = Depends(protect)):
    try:
        cursor = getCursor()
        cursor.execute(
            """
            SELECT _id, user_id, summary, category_scores, answers, created_at, updated_at
            FROM assessment_results
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user["id"],),
        )
        rows = cursor.fetchall() or []
        cursor.close()

        def _maybe_load(v):
            if isinstance(v, str):
                try:
                    return json.loads(v)
                except Exception:
                    return v
            return v

        history = []
        for rid, uid, summ, cats, ans, ca, ua in rows:
            history.append(
                {
                    "_id": str(rid),
                    "user": uid,
                    "summary": _maybe_load(summ),
                    "category_scores": _maybe_load(cats),
                    "answers": _maybe_load(ans),
                    "created_at": ca.isoformat() if hasattr(ca, "isoformat") else ca,
                    "updated_at": ua.isoformat() if hasattr(ua, "isoformat") else ua,
                }
            )

        return JSONResponse(status_code=200, content=history)

    except Exception as err:
        print("FETCH HISTORY ERROR:", err)
        return JSONResponse(status_code=500, content={"error": "Failed to fetch history"})


@router.get("/{id}/download")
async def download_pdf(id: str, user: dict = Depends(protect)):
    try:
        cursor = getCursor()
        cursor.execute(
            """
            SELECT _id, user_id, summary, category_scores, answers, created_at, updated_at
            FROM assessment_results
            WHERE _id::text = %s
            """,
            (id,),
        )
        row = cursor.fetchone()
        cursor.close()

        if not row:
            raise HTTPException(status_code=404, detail="Assessment not found")

        rid, uid, summ, cats, ans, created_at, updated_at = row
        if uid != user["id"]:
            raise HTTPException(status_code=403, detail="Forbidden")

        def _maybe_load(v):
            if isinstance(v, str):
                try:
                    return json.loads(v)
                except Exception:
                    return v
            return v

        assessment = {
            "_id": str(rid),
            "user": uid,
            "summary": _maybe_load(summ),
            "category_scores": _maybe_load(cats),
            "answers": _maybe_load(ans),
            "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else created_at,
            "updated_at": updated_at.isoformat() if hasattr(updated_at, "isoformat") else updated_at,
        }

        pdf_bytes = generate_assessment_pdf_bytes(assessment)
        filename = f"assessment-{assessment['_id']}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

