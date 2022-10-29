from typing import List

from fastapi import APIRouter, HTTPException, status
from starlette.responses import FileResponse

from src.config import UserIdeaRelations, FILES_PATH
from src.api.schemas import OkResponse
from src.database.repositories import IDEA, USERIDEARELATIONS, USER
from src.database.schemas import Idea

router = APIRouter(prefix="/telegram", tags=["Telegram"])


async def check_telegram(telegram_username):
    try:
        user = await USER.get_by_telegram(telegram=telegram_username)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram not found",
        )
    return user


@router.post("/like")
async def like_idea(*,
                    telegram_username: str,
                    idea_id: int) -> OkResponse:
    user = await check_telegram(telegram_username=telegram_username)

    like_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=user.id,
                                                                 idea_id=idea_id,
                                                                 relation=UserIdeaRelations.like)

    if like_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Like exist",
        )

    relation = await USERIDEARELATIONS.add(
        user_id=user.id,
        idea_id=idea_id,
        relation=UserIdeaRelations.like
    )

    await IDEA.safe_increase_like(
        idea_id=idea_id
    )

    if not relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while modifying base",
        )

    return OkResponse()


@router.post("/dislike")
async def dislike_idea(*,
                       telegram_username: str,
                       idea_id: int) -> OkResponse:
    user = await check_telegram(telegram_username=telegram_username)

    dislike_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=user.id,
                                                                    idea_id=idea_id,
                                                                    relation=UserIdeaRelations.dislike)

    if dislike_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dislike exist",
        )

    relation = await USERIDEARELATIONS.add(
        user_id=user.id,
        idea_id=idea_id,
        relation=UserIdeaRelations.dislike
    )

    if not relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while modifying base",
        )

    return OkResponse()


@router.post("/request_membership")
async def request_membership(*,
                             telegram_username: str,
                             idea_id: int) -> OkResponse:
    user = await check_telegram(telegram_username=telegram_username)

    request_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=user.id,
                                                                    idea_id=idea_id,
                                                                    relation=UserIdeaRelations.request_membership)
    member_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=user.id,
                                                                   idea_id=idea_id,
                                                                   relation=UserIdeaRelations.member)

    if request_exist or member_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already in team or sent request",
        )

    relation = await USERIDEARELATIONS.add(
        user_id=user.id,
        idea_id=idea_id,
        relation=UserIdeaRelations.request_membership
    )

    if not relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while modifying base",
        )

    return OkResponse()


@router.get("/get_unwatched_idea")
async def get_unwatched_ideas(*,
                              telegram_username: str) -> List[Idea]:
    user = await check_telegram(telegram_username=telegram_username)
    ideas = await IDEA.get_approved()
    relations = await USERIDEARELATIONS.get_all_by_user_id(user_id=user.id)
    relations_ids = [relation.idea_id for relation in relations]
    result = [idea for idea in ideas if idea.id not in relations_ids]

    if len(result) == 0:
        raise HTTPException(detail="No ideas to show", status_code=status.HTTP_404_NOT_FOUND)

    return result[0]