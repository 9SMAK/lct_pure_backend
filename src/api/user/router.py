from fastapi import APIRouter, Depends
from src.database.repositories import USERIDEARELATIONS
from src.config import UserIdeaStatus

router = APIRouter(prefix="/user", tags=["User"])


# @router.get('/liked')
# async def get_liked_ideas():
    # result = await USERIDEARELATIONS.get_by_id(id=user_id
    #                                            relation=UserIdeaStatus.like)
    # return result
