from fastapi import APIRouter, Request
from api.webhooks.schemas import ScannerWebhookRequest, ScannerWebhookResultRequest
from db.base import getCursor
import json

router = APIRouter(prefix='/webhooks')


@router.post("/scan/notification")
def scanner_webhook(request: ScannerWebhookRequest):
    data = request.data
    print(f"Received scanner webhook: {data}")


@router.post("/scan/result")
async def scan_result_webhook(request: Request):
    body = await request.json()
    print("----- Scan Completed -----")
    scan_id = body["scan_id"]

    cursor = getCursor()
    cursor.execute(
        """
        UPDATE scan_results
        SET results = %s,
        updated_at = now()
        WHERE scan_id = %s
        """,
        (
            json.dumps(body),
            scan_id,
        ),
    )
    cursor.close()

    return {"status": "ok"}
    