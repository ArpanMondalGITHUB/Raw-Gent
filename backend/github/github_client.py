import httpx
from core.config import GITHUB_CLIENT_ID , GITHUB_CLIENT_SECRET

async def get_github_access_token(code: str):
    url = "https://github.com/login/oauth/access_token"

    payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code
    }
    print(f"payload:{payload}")
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    

async def get_github_user(access_token:str):

    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com/user",headers=headers)
        response.raise_for_status()
        return response.json()
    

async def get_user_repo_list(access_token:str):
    url = "https://api.github.com/user/repos"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url,headers=headers)
        response.raise_for_status()
        return response.json()
    


async def get_user_org_repo_list(access_token:str,org:str,type:str,sort:str):

    url = f"https://api.github.com/orgs/{org}/repos"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    params = {
        "type": type,
        "sort": sort
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url,headers=headers,params=params)
        response.raise_for_status()
        return response.json()
