from contextlib import asynccontextmanager
from fastapi import FastAPI 
from backend.routes import agent_runner_routes, internal_routes
from routes import auth_routes , webhook , add_repo_route
from fastapi.middleware.cors import CORSMiddleware
from core.config import FRONTEND_URL
from services.redis import redisservices

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
app.include_router(internal_routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
