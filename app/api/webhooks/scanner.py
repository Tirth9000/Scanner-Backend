from fastapi import APIRouter, Request
from api.webhooks.schemas import ScannerWebhookRequest, ScannerWebhookResultRequest

router = APIRouter()


@router.post("/webhooks/scan/notification")
def scanner_webhook(request: ScannerWebhookRequest):
    data = request.data
    print(f"Received scanner webhook: {data}")
    return {"status": "ok"}


@router.post("/webhooks/scan/result")
async def scan_result_webhook(request: Request):
    body = await request.json()
    print(body)
    return {"status": "ok"}
    