from fastapi import APIRouter
from src.database.repositories import USER, IDEA, USERIDEARELATIONS
from src.database.schemas import User
from src.api.schemas import OkResponse

router = APIRouter(prefix="/database", tags=["Database"])


@router.get("/create_all")
async def create_all():
    await USER.create_repository()
    await IDEA.create_repository()
    await USERIDEARELATIONS.create_repository()
    return OkResponse()


@router.get("/drop_all")
async def drop_all():
    await USER.create_repository()
    await IDEA.delete_repository()
    await USERIDEARELATIONS.delete_repository()
    return OkResponse()


@router.get("/create_users")
async def create_users():
    await USER.create_repository()
    return OkResponse()


@router.get("/drop_users")
async def drop_users():
    await USER.delete_repository()
    return OkResponse()


@router.get("/get_all_users")
async def get_all_users():
    result = await USER.get_all()
    return result


@router.get("/get_user_by_id")
async def get_user_by_id(user_id: int) -> User:
    result = await USER.get_by_id(id=user_id)
    return result


@router.get("/create_ideas")
async def create_ideas():
    await IDEA.create_repository()
    return OkResponse()


@router.get("/drop_ideas")
async def drop_ideas():
    await IDEA.delete_repository()
    return OkResponse()


@router.get("/get_all_ideas")
async def get_all_ideas():
    result = await IDEA.get_all()
    return result