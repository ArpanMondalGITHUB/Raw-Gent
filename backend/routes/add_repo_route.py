from fastapi import APIRouter , Request
from fastapi.responses import JSONResponse
from services.github_app_service import get_repos_from_installation , get_repo_branches

router = APIRouter()


@router.get("/installation-repos")
async def list_installation_repos(request: Request):
    print("🧪 Incoming cookies:", request.cookies)
    installation_id = request.cookies.get("installation_id")
    if not installation_id:
        return JSONResponse({"error": "GitHub App not installed or installation_id missing"}, status_code=400)

    try:
        repos_data = await get_repos_from_installation(installation_id)
        return JSONResponse({"repositories": repos_data["repositories"]})
    except Exception as e:
        print(f"[ERROR] Failed to get repos from installation: {e}")
        return JSONResponse({"error": "Failed to fetch repositories"}, status_code=500)
    

@router.get("/branches/{repo_name}")
async def name(repo_name:str,request:Request):
    installation_id = request.cookies.get("installation_id")
    if not installation_id:
        return JSONResponse({"error": "No installation ID"}, status_code=400)
    
    try:
      branches = await get_repo_branches(installation_id,repo_name)
      return JSONResponse({"Branches":branches})
    except Exception as e:
        print(f"[ERROR] Failed to get repos from installation: {e}")
        return JSONResponse({"error": "Failed to fetch repositories"}, status_code=500)