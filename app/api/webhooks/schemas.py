from pydantic import BaseModel
from typing import Any
import time


class ScannerWebhookRequest(BaseModel):
    scan_id: str
    event: str
    data: str

class ScannerWebhookResultRequest(BaseModel):
    scan_id: str
    target: str
    data: Any
    # timestamp: str

