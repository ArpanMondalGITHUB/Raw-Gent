from fastapi import APIRouter , Request
from starlette.responses import RedirectResponse , JSONResponse
from auth import get_github_authorization_url
from services.github_app_service import get_repos_from_installation, get_user_installation_id
from github.github_app_client import generate_jwt, get_installation_access_token
from github.github_client import get_github_access_token , get_github_user , get_user_repo_list

router = APIRouter()

@router.get('/login')
def login():
    url = get_github_authorization_url()
    print(f"url:{url}")
    return RedirectResponse(url)

@router.get("/auth/callback")
async def auth_callback(request:Request):
    code = request.query_params.get("code")
    print(f"code:{code}")
    if not code:
        return JSONResponse({"error": "Missing code"}, status_code=400)
    
    token_data = await get_github_access_token(code)
    print(f"token data:{token_data}")
    access_token = token_data.get("access_token")
    if not access_token:
        return JSONResponse({"error":"Token exchange failed"},status_code=400)
    
    user_data = await get_github_user(access_token)

    response = RedirectResponse("https://rawgent.vercel.app/home")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="None",
        domain=".ngrok-free.app"
    )
    return response


@router.get("/callback")
async def github_app_callback(request: Request):
    installation_id = request.query_params.get("installation_id")
    if not installation_id:
        return JSONResponse({"error": "Missing installation_id"}, status_code=400)

    return RedirectResponse(f"/redirect-home?installation_id={installation_id}")   


@router.get("/redirect-home")
async def redirect_home(request: Request):
    installation_id = request.query_params.get("installation_id")
    print("📦 Redirect-home installation_id:", installation_id)

    response = RedirectResponse("https://rawgent.vercel.app/home")

    if installation_id:
        response.set_cookie(
            key="installation_id",
            value=installation_id,
            httponly=True,
            secure=True,  # ✅ because you're now on HTTPS (ngrok)
            samesite="None",  # ✅ must be 'None' to send across domains
            domain=".ngrok-free.app"  # ✅ this is crucial
        )

    return response



@router.get("/welcome")
async def welcome(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    return JSONResponse({"message": "Welcome! You're logged in with GitHub."})


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



# @router.get("/user-repos")
# async def get_repos(request: Request):
#     token = request.cookies.get("access_token")
#     if not token:
#         return JSONResponse({"error":"Not authenticated"},status_code=400)
    
#     try:
#       repos_data = await get_user_repo_list(token)
#       return JSONResponse(repos_data)
#     except Exception as e:
#         return JSONResponse({"error": "Failed to fetch repositories"}, status_code=500)
