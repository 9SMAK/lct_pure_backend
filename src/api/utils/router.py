from fastapi import APIRouter
from src.database.repositories import SKILL, IDEATAG

router = APIRouter(prefix="/utils", tags=["Utils"])


@router.get('/get_skills')
async def get_skills():
    result = await SKILL.get_all()
    return result


@router.get('/get_idea_tags')
async def get_idea_tags():
    result = await IDEATAG.get_all()
    return result
