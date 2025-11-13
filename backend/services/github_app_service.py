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


async def get_repo_branches(installation_id:str , repo_name:str):
    jwt_token = generate_jwt()
    access_token_data = await get_installation_access_token(jwt_token, installation_id)
    token = access_token_data["token"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    async with httpx.AsyncClient() as client:
        # First, get all repositories for this installation to find the owner
        repos_response = await client.get(
            "https://api.github.com/installation/repositories",
            headers=headers
        )
        repos_response.raise_for_status()
        repositories = repos_response.json()["repositories"]
        
        # Find the repository to get its owner
        target_repo = None
        for repo in repositories:
            if repo["name"] == repo_name:
                target_repo = repo
                break
        
        if not target_repo:
            raise Exception(f"Repository '{repo_name}' not found in installation")
        
        owner = target_repo["owner"]["login"]
        
        # Now fetch branches using the correct owner
        branches_response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo_name}/branches",
            headers=headers,
            params={
                "per_page": 100  # Get up to 100 branches
            }
        )
        branches_response.raise_for_status()
        return branches_response.json()


async def mint_installation_token(installation_id: str) -> str:
    """Return a short-lived installation access token for a given installation_id."""
    jwt_token = generate_jwt()
    access_token_data = await get_installation_access_token(jwt_token, installation_id)
    return access_token_data["token"]
        