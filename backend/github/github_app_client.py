import jwt as pyjwt
import time
from core.config import GITHUB_APP_CLIENT_ID, GITHUB_PRIVATE_KEY_PATH
import httpx

print(f"GITHUB_APP_ID :{GITHUB_APP_CLIENT_ID} , GITHUB_PRIVATE_KEY_PATH : {GITHUB_PRIVATE_KEY_PATH}")


def generate_jwt():
    now = int(time.time())
    with open(GITHUB_PRIVATE_KEY_PATH, "rb") as f:
        private_key = f.read()

    payload = {
        "iat": now,
        "exp": now + 600,
        "iss": GITHUB_APP_CLIENT_ID
    }
    print(f"payload:{payload}")
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


