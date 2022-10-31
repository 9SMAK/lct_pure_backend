from fastapi import APIRouter

from src.api.schemas import OkResponse
from src.database.repositories import USER, IDEA, SKILL, IDEATAG
from src.database.schemas import User, Skill, IdeaTag

router = APIRouter(prefix="/utils", tags=["Utils"])


@router.get('/get_skills', response_model=Skill)
async def get_skills():
    result = await SKILL.get_all()
    return result


@router.get('/get_idea_tags', response_model=IdeaTag)
async def get_idea_tags():
    result = await IDEATAG.get_all()
    return result


