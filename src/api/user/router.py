import uuid
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Body

from src.api.helpers import async_upload_file, remove_file
from src.api.idea.schemas import TeamRequest
from src.database.repositories import USERIDEARELATIONS, IDEA, USER, SKILLTOUSER, USERPREFERENCES
from src.api.auth.authentication import AuthenticatedUser, get_current_user
from src.api.schemas import OkResponse
from src.config import RelationsTypes
from src.api.user.schemas import EditProfileRequest, EditSkillsRequest
from src.database.schemas import Idea, SkillToUser, User

router = APIRouter(prefix="/user", tags=["User"])


@router.post('/edit_profile', response_model=OkResponse)
async def edit_profile(*, current_user: AuthenticatedUser = Depends(get_current_user),
                       avatar: UploadFile = None,
                       edit_info: EditProfileRequest = Body(...)) -> OkResponse:
    user = await USER.get_by_id(current_user.id)

    if avatar:
        if user.avatar_id is None:
            avatar_id = str(uuid.uuid4())
            await USER.edit_profile(current_user.id, avatar_id=avatar_id)
        else:
            await remove_file(user.avatar_id)
            avatar_id = user.avatar_id

        await async_upload_file(file=avatar,
                                file_id=avatar_id,
                                ext='.jpg')

    result = await USER.edit_profile(current_user.id, **edit_info.dict(exclude_none=True))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while editing profile",
        )
    return OkResponse()


@router.post('/edit_skills', response_model=OkResponse)
async def edit_skills(*, current_user: AuthenticatedUser = Depends(get_current_user),
                      weights: List[EditSkillsRequest]) -> OkResponse:
    for skill in weights:
        result = await SKILLTOUSER.add(
            skill_id=int(skill.id),
            user_id=current_user.id,
            weight=skill.weight
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error while editing profile",
            )
    return OkResponse()


@router.post('/edit_preferences', response_model=OkResponse)
async def edit_preferences(*, current_user: AuthenticatedUser = Depends(get_current_user),
                           weights: List[EditSkillsRequest]) -> OkResponse:
    for skill in weights:
        result = await USERPREFERENCES.add(
            tag_id=int(skill.id),
            user_id=current_user.id,
            weight=skill.weight
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error while editing profile",
            )
    return OkResponse()


@router.post('/accept_request', response_model=OkResponse)
async def accept_request(*, current_user: AuthenticatedUser = Depends(get_current_user),
                         user_id: int,
                         idea_id: int) -> OkResponse:
    idea = await IDEA.get_by_id(id=idea_id)
    # check if not author
    if not current_user.id == idea.author_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not author",
        )

    await USERIDEARELATIONS.accept_membership(idea_id=idea.id, user_id=user_id)
    return OkResponse()


@router.get('/get_my_skills', response_model=List[SkillToUser])
async def get_skills(current_user: AuthenticatedUser = Depends(get_current_user)):
    skills = await SKILLTOUSER.get_by_user_id(user_id=current_user.id)
    return skills


@router.get('/liked_ideas', response_model=List[Idea])
async def get_liked_ideas(current_user: AuthenticatedUser = Depends(get_current_user)) -> List[Idea]:
    result = []
    relations = await USERIDEARELATIONS.get_all_relations_by_user_id(user_id=current_user.id,
                                                                     relation=RelationsTypes.like)
    for relation in relations:
        result.append(await IDEA.get_by_id(relation.idea_id))
    return result


@router.get('/disliked_ideas', response_model=List[Idea])
async def get_disliked_ideas(current_user: AuthenticatedUser = Depends(get_current_user)) -> List[Idea]:
    result = []
    relations = await USERIDEARELATIONS.get_all_relations_by_user_id(user_id=current_user.id,
                                                                     relation=RelationsTypes.dislike)
    for relation in relations:
        result.append(await IDEA.get_by_id(relation.idea_id))
    return result


@router.get("/get_requests_in_team", response_model=List[TeamRequest])
async def get_requests_in_team(*,
                               current_user: AuthenticatedUser = Depends(get_current_user)) -> List[TeamRequest]:
    ideas = await IDEA.get_my_ideas(current_user.id)

    result = []
    for idea in ideas:
        relations = await USERIDEARELATIONS.get_all_members_requests(idea_id=idea.id)
        requests = [await USER.get_by_id(id=relation.user_id) for relation in relations]
        result.append(TeamRequest(idea=idea, requests=requests))
    return result


@router.get("/get_all_users", response_model=List[User])
async def get_all_users():
    result = await USER.get_all()
    return result


@router.get("/get_user_by_id", response_model=User)
async def get_user_by_id(user_id: int) -> User:
    result = await USER.get_by_id(id=user_id)
    return result
