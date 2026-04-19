from urllib.parse import urlencode

from core.config import GITHUB_CALLBACK_URL, GITHUB_CLIENT_ID

def get_github_authorization_url():
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "scope": "repo,user:email",
    }

    if GITHUB_CALLBACK_URL:
        params["redirect_uri"] = GITHUB_CALLBACK_URL

    return f"https://github.com/login/oauth/authorize?{urlencode(params)}"

