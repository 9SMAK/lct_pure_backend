from fastapi import APIRouter
from src.database.repositories import USER, IDEA, USERIDEARELATIONS, COMMENT, SKILL, SKILLTOUSER, IDEATAG, TAGTOIDEA
from src.database.schemas import User
from src.api.schemas import OkResponse

router = APIRouter(prefix="/database", tags=["Database"])

name_to_repo = {
    "USER": USER,
    "IDEA": IDEA,
    "SKILL": SKILL,
    "SKILLTOUSER": SKILLTOUSER,
    "USERIDEARELATIONS": USERIDEARELATIONS,
    "COMMENT": COMMENT,
    "IDEATAG": IDEATAG,
    "TAGTOIDEA": TAGTOIDEA,
}


@router.get("/create_all")
async def create_all():
    await USER.create_repository()
    await IDEA.create_repository()
    await SKILL.create_repository()
    await IDEATAG.create_repository()
    await TAGTOIDEA.create_repository()
    await SKILLTOUSER.create_repository()
    await USERIDEARELATIONS.create_repository()
    await COMMENT.create_repository()
    return OkResponse()


@router.get("/drop_all")
async def drop_all():
    await USERIDEARELATIONS.delete_repository()
    await COMMENT.delete_repository()
    await IDEA.delete_repository()
    await USER.delete_repository()
    await IDEATAG.delete_repository()
    await SKILL.delete_repository()
    await SKILLTOUSER.delete_repository()
    await TAGTOIDEA.delete_repository()
    return OkResponse()


@router.get("/refresh_table")
async def refresh_table(table_name: str):
    repo = name_to_repo[table_name]
    await repo.delete_repository()
    await repo.create_repository()
    return OkResponse()


@router.get("/create_table")
async def create_table(table_name: str):
    repo = name_to_repo[table_name]
    await repo.create_repository()
    return OkResponse()


@router.get("/drop_table")
async def drop_table(table_name: str):
    repo = name_to_repo[table_name]
    await repo.delete_repository()
    return OkResponse()


@router.get("/get_table_elems")
async def get_table_elems(table_name: str):
    result = await name_to_repo[table_name].get_all()
    return result


@router.get("/get_all_users")
async def get_all_users():
    result = await USER.get_all()
    return result


@router.get("/get_user_by_id")
async def get_user_by_id(user_id: int) -> User:
    result = await USER.get_by_id(id=user_id)
    return result
