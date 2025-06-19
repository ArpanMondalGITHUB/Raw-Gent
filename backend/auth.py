from core.config import GITHUB_CLIENT_ID

def get_github_authorization_url():
    return (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&scope=repo,user:email"  # not just "user"
    )

