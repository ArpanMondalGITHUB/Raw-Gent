import jwt as pyjwt
import time
from pathlib import Path

from core.config import GITHUB_APP_CLIENT_ID, GITHUB_PRIVATE_KEY, GITHUB_PRIVATE_KEY_PATH
import httpx


def _load_private_key() -> str:
    if GITHUB_PRIVATE_KEY:
        return GITHUB_PRIVATE_KEY.replace("\\n", "\n")

    if GITHUB_PRIVATE_KEY_PATH:
        return Path(GITHUB_PRIVATE_KEY_PATH).read_text(encoding="utf-8")

    raise RuntimeError("Missing GITHUB_PRIVATE_KEY or GITHUB_PRIVATE_KEY_PATH")


def generate_jwt():
    now = int(time.time())
    private_key = _load_private_key()

    payload = {
        "iat": now,
        "exp": now + 600,
        "iss": GITHUB_APP_CLIENT_ID
    }
    return pyjwt.encode(payload, private_key, algorithm="RS256")
    

async def get_installation_access_token(jwt_token, installation_id):
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)
        response.raise_for_status()
        return response.json()


