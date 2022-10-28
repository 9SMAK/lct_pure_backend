from fastapi import APIRouter

from src.api.schemas import OkResponse
from src.database.repositories import USER, IDEA
from src.database.schemas import User

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post('/approve_idea')
async def approve_idea(idea_id: int) -> OkResponse:
    await IDEA.approve_idea(idea_id=idea_id)
    return OkResponse()
