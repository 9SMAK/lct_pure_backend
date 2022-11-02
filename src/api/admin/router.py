from fastapi import APIRouter

from src.api.schemas import OkResponse
from src.database.repositories import IDEA, SKILL, IDEATAG

router = APIRouter(prefix="/admin", tags=["Admin"])


# TODO check if admin
@router.post('/approve_idea', response_model=OkResponse)
async def approve_idea(id: int) -> OkResponse:
    await IDEA.approve_idea(idea_id=id)
    return OkResponse()


@router.post('/add_skill', response_model=OkResponse)
async def add_skill(name: str) -> OkResponse:
    await SKILL.add(name=name)
    return OkResponse()


@router.post('/add_idea_tag', response_model=OkResponse)
async def add_idea_tag(name: str) -> OkResponse:
    await IDEATAG.add(name=name)
    return OkResponse()
