from fastapi import FastAPI, Request, HTTPException

app = FastAPI()


@app.post("/webhooks/scanner")
def scanner_webhook(request: Request):
    pass