from fastapi import APIRouter

from src.api.schemas import OkResponse
from src.database.repositories import USER, IDEA
from src.database.schemas import User

router = APIRouter(prefix="/admin", tags=["Admin"])
