from contextlib import asynccontextmanager
from fastapi import FastAPI 
from routes import agent_runner_routes
from routes import auth_routes , webhook , add_repo_route
from fastapi.middleware.cors import CORSMiddleware
from core.config import CORS_ORIGINS, RATE_LIMIT_ENABLED
from services.redis import redisservices
from services.rate_limit_middleware import RateLimitMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting FastAPI app...")
    await redisservices.connect()
    print("✅ Redis connected")
    try:
        yield
    finally:
        print("🛑 Shutting down...")
        await redisservices.close()

app = FastAPI(lifespan=lifespan)

app.include_router(auth_routes.router)
app.include_router(webhook.router)
app.include_router(add_repo_route.router)
app.include_router(agent_runner_routes.router)


@app.get("/health")
async def health():
    return {"status": "ok"}

# Order matters: the last-added middleware is outermost. Add the rate limiter
# first and CORS last so CORS wraps it and 429 responses keep CORS headers
# (otherwise browsers can't read the rejection).
if RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
