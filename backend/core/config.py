import os
from dotenv import load_dotenv

load_dotenv()

# OAuth App
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
print(f"GITHUB_CLIENT_ID:{GITHUB_CLIENT_ID}")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
print(f"GITHUB_CLIENT_SECRET:{GITHUB_CLIENT_SECRET}")

# GitHub App
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
print(f"GITHUB_APP_ID:{GITHUB_APP_ID}")
GITHUB_APP_CLIENT_ID = os.getenv("GITHUB_APP_CLIENT_ID")
print(f"GITHUB_APP_CLIENT_ID:{GITHUB_APP_CLIENT_ID}")
GITHUB_APP_CLIENT_SECRET = os.getenv("GITHUB_APP_CLIENT_SECRET")
print(f"GITHUB_APP_CLIENT_SECRET:{GITHUB_APP_CLIENT_SECRET}")
GITHUB_PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")
print(f"GITHUB_PRIVATE_KEY_PATH:{GITHUB_PRIVATE_KEY_PATH}")
