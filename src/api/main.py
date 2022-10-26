import os

from fastapi import FastAPI, APIRouter, Depends
import src.config as cfg
 
from src.api.user import router as user_router
from src.api.admin import router as admin_router
from src.api.schemas import HomePageResponse, ResponseStatus, SqlReturn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")
api_router.include_router(user_router.router)
api_router.include_router(admin_router.router)
app.include_router(api_router)


@app.get("/homepage/{username}")
async def homepage(username: str):
    print(os.getenv("POSTGRES_URL"), os.getenv("POSTGRES_DB"))
    return HomePageResponse(username=username, message=f"Hello, {username}, {os.getenv('POSTGRES_DB')}")
