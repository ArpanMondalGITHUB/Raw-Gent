from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/webhook")
async def github_webhook(request: Request):
    body = await request.json()
    print("🔔 Webhook Event Received:", body)

    # TODO: add logic here to handle PRs, issues, etc.

    return JSONResponse({"message": "Webhook received"}, status_code=200)
