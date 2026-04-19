from fastapi import APIRouter , Request
from starlette.responses import RedirectResponse , JSONResponse
from auth import get_github_authorization_url
from github.github_client import get_github_access_token , get_github_user 
from core.config import (
    COOKIE_ACCESS_NAME,
    COOKIE_DOMAIN,
    COOKIE_INSTALLATION_NAME,
    COOKIE_PATH,
    COOKIE_SAMESITE,
    COOKIE_SECURE,
    FRONTEND_URL,
)
router = APIRouter()


def _cookie_options() -> dict:
    options = {
        "httponly": True,
        "secure": COOKIE_SECURE,
        "samesite": COOKIE_SAMESITE,
        "path": COOKIE_PATH,
    }

    if COOKIE_DOMAIN:
        options["domain"] = COOKIE_DOMAIN

    return options


def _frontend_home_url() -> str:
    return f"{FRONTEND_URL}/home" if FRONTEND_URL else "/home"

@router.get('/login')
def login():
    url = get_github_authorization_url()
    return RedirectResponse(url)

@router.get("/auth/callback")
async def auth_callback(request:Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "Missing code"}, status_code=400)
    
    token_data = await get_github_access_token(code)
    access_token = token_data.get("access_token")
    if not access_token:
        return JSONResponse({"error":"Token exchange failed"},status_code=400)
    
    await get_github_user(access_token)

    response = RedirectResponse(_frontend_home_url())
    response.set_cookie(
        key=COOKIE_ACCESS_NAME,
        value=access_token,
        **_cookie_options(),
    )
    return response

@router.get("/welcome")
async def welcome(request: Request):
    token = request.cookies.get(COOKIE_ACCESS_NAME)
    if not token:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    return JSONResponse({"message": "Welcome! You're logged in with GitHub."})


@router.get("/callback")
async def github_app_callback(request: Request):
    installation_id = request.query_params.get("installation_id")
    if not installation_id:
        return JSONResponse({"error": "Missing installation_id"}, status_code=400)

    return RedirectResponse(f"/redirect-home?installation_id={installation_id}")   


@router.get("/redirect-home")
async def redirect_home(request: Request):
    installation_id = request.query_params.get("installation_id")
    return RedirectResponse(f"/set-cookie?installation_id={installation_id}")


@router.get("/set-cookie")
async def set_cookie_and_redirect(request:Request):
    installation_id = request.query_params.get("installation_id")
    response = RedirectResponse(_frontend_home_url())

    response.set_cookie(
        key=COOKIE_INSTALLATION_NAME,
        value=installation_id,
        **_cookie_options(),
    )
    return response


