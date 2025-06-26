from fastapi import FastAPI 
from routes import auth_routes , webhook
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(auth_routes.router)
app.include_router(webhook.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://raw-gent.vercel.app/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"Hello world"}