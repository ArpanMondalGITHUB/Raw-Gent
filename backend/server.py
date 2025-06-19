from fastapi import FastAPI 
from routes import auth_routes , webhook

app = FastAPI()

app.include_router(auth_routes.router)
app.include_router(webhook.router)

@app.get("/")
async def home():
    return {"Hello world"}