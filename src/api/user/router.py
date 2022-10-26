from fastapi import APIRouter, Depends
from src.api.user.schemas import UserAuthData
from src.database.repositories import USER
from src.database.schemas import User

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/create")
async def add_user(login: str, password: str):
    res = await USER.add(login=login, hashed_password=password)
    return res


@router.get("/get_user_by_id")
async def get_user_by_id(user_id: int) -> User:
    result = await USER.get_by_id(user_id=user_id)
    return result
