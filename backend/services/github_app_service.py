import httpx
from github.github_app_client import generate_jwt, get_installation_access_token

async def get_user_installation_id(user_token: str) -> str | None:
    url = "https://api.github.com/user/installations"
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        print("Status:", response.status_code)
        print("Installations response:", response.text)
        if response.status_code != 200:
            return None
        
        installations = response.json().get("installations", [])
        if not installations:
            return None
        
        return installations[0]["id"] # Pick the first for now

async def get_repos_from_installation(installation_id: str) -> dict:
    jwt_token = generate_jwt()
    access_token_data = await get_installation_access_token(jwt_token, installation_id)
    installation_access_token = access_token_data.get("token")

    headers = {
        "Authorization": f"Bearer {installation_access_token}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/installation/repositories", headers=headers
        )
        response.raise_for_status()
        repos_data = response.json()
        print("repos_data:", repos_data)
        return repos_data
