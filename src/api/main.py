from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from src.api.user import router as user_router
from src.api.auth import router as auth_router
from src.api.admin import router as admin_router
from src.api.idea import router as idea_router
from src.api.utils import router as utils_router
from src.api.telegram import router as telegram_router
from src.api.fill import router as fake_router
from src.api.static import router as static_router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")
api_router.include_router(idea_router.router)
api_router.include_router(user_router.router)
api_router.include_router(auth_router.router)
api_router.include_router(admin_router.router)
api_router.include_router(utils_router.router)
api_router.include_router(static_router.router)
api_router.include_router(telegram_router.router)
api_router.include_router(fake_router.router)
app.include_router(api_router)