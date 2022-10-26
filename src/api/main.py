import os

from fastapi import FastAPI, APIRouter, Depends
import src.config as cfg

from src.api.user import router as user_router
from src.api.auth import router as auth_router
from src.api.admin import router as admin_router
from src.api.schemas import HomePageResponse, ResponseStatus, SqlReturn
from fastapi.middleware.cors import CORSMiddleware
from src.api.auth.authentication import authenticate_user, create_access_token, get_current_user, get_password_hash, \
    AuthenticatedUser

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")
# api_router.include_router(user_router.router)
api_router.include_router(admin_router.router)
api_router.include_router(auth_router.router)
app.include_router(api_router)