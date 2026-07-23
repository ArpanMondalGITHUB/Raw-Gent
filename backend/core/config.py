import os
from dotenv import load_dotenv

load_dotenv()

def _clean_env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None

    value = value.strip()
    return value or None


def _get_bool_env(name: str, default: bool) -> bool:
    value = _clean_env(name)
    if value is None:
        return default

    return value.lower() in {"1", "true", "yes", "on"}


def _get_int_env(name: str, default: int) -> int:
    value = _clean_env(name)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default


def _get_csv_env(name: str) -> list[str]:
    value = _clean_env(name)
    if not value:
        return []

    return [item.strip() for item in value.split(",") if item.strip()]


def _url_uses_https(value: str | None) -> bool:
    return bool(value and value.lower().startswith("https://"))


# OAuth App
GITHUB_CLIENT_ID = _clean_env("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = _clean_env("GITHUB_CLIENT_SECRET")
GITHUB_CALLBACK_URL = _clean_env("GITHUB_CALLBACK_URL")

# GitHub App
GITHUB_APP_ID = _clean_env("GITHUB_APP_ID")
GITHUB_APP_CLIENT_ID = _clean_env("GITHUB_APP_CLIENT_ID")
GITHUB_APP_CLIENT_SECRET = _clean_env("GITHUB_APP_CLIENT_SECRET")
GITHUB_PRIVATE_KEY_PATH = _clean_env("GITHUB_PRIVATE_KEY_PATH")
GITHUB_PRIVATE_KEY = _clean_env("GITHUB_PRIVATE_KEY")

# LLM
GEMINI_API_KEY = _clean_env("GEMINI_API_KEY")

# JOB ENV
GCP_PROJECT_ID = _clean_env("GCP_PROJECT_ID")
GCP_REGION = _clean_env("GCP_REGION")
CLOUD_RUN_JOB = _clean_env("CLOUD_RUN_JOB")
JOB_RUNNER_MODE = (_clean_env("JOB_RUNNER_MODE") or "cloud_run").lower()
JOB_QUEUE_NAME = _clean_env("JOB_QUEUE_NAME") or "agent_jobs:queue"

# FrontEnd URL
FRONTEND_URL = _clean_env("FRONTEND_URL")

# Backend URL
BACKEND_URL = _clean_env("BACKEND_URL")
REDIS_URL = _clean_env("REDIS_URL") or "redis://localhost:6379/0"
REDIS_SSL_VERIFY = _get_bool_env("REDIS_SSL_VERIFY", REDIS_URL.startswith("rediss://"))

# Rate limiting (Redis-backed, fixed-window)
RATE_LIMIT_ENABLED = _get_bool_env("RATE_LIMIT_ENABLED", True)
RATE_LIMIT_REQUESTS = _get_int_env("RATE_LIMIT_REQUESTS", 100)
RATE_LIMIT_WINDOW_SECONDS = _get_int_env("RATE_LIMIT_WINDOW_SECONDS", 60)

# HTTP / CORS
CORS_ORIGINS = _get_csv_env("CORS_ORIGINS")
if not CORS_ORIGINS and FRONTEND_URL:
    CORS_ORIGINS = [FRONTEND_URL]

# Cookies
COOKIE_DOMAIN = _clean_env("COOKIE_DOMAIN")
COOKIE_PATH = _clean_env("COOKIE_PATH") or "/"
COOKIE_SECURE = _get_bool_env(
    "COOKIE_SECURE",
    _url_uses_https(FRONTEND_URL) or _url_uses_https(BACKEND_URL),
)
COOKIE_SAMESITE = (_clean_env("COOKIE_SAMESITE") or "lax").lower()
COOKIE_ACCESS_NAME = _clean_env("COOKIE_ACCESS_NAME") or "access_token"
COOKIE_INSTALLATION_NAME = _clean_env("COOKIE_INSTALLATION_NAME") or "installation_id"
