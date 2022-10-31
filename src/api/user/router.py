from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from src.database.repositories import USERIDEARELATIONS, IDEA, USER, SKILLTOUSER
from src.api.auth.authentication import AuthenticatedUser, get_current_user
from src.api.schemas import OkResponse
from src.config import UserIdeaRelations
from src.api.user.schemas import EditProfileRequest
from src.database.schemas import Idea, SkillToUser

router = APIRouter(prefix="/user", tags=["User"])


@router.post('/edit_profile', response_model=OkResponse)
async def edit_profile(*, current_user: AuthenticatedUser = Depends(get_current_user),
                       edit_info: EditProfileRequest) -> OkResponse:
    result = await USER.edit_profile(current_user.id, **edit_info.dict(exclude_none=True))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while editing profile",
        )
    return OkResponse()


@router.post('/edit_skills', response_model=OkResponse)
async def edit_skills(*, current_user: AuthenticatedUser = Depends(get_current_user),
                      weights: Dict) -> OkResponse:
    for skill_id, weight in weights.items():
        result = await SKILLTOUSER.add(
            skill_id=int(skill_id),
            user_id=current_user.id,
            weight=weight
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error while editing profile",
            )
    return OkResponse()


@router.get('/get_my_skills', response_model=List[SkillToUser])
async def get_skills(current_user: AuthenticatedUser = Depends(get_current_user)):
    skills = await SKILLTOUSER.get_by_user_id(user_id=current_user.id)
    return skills


@router.get('/liked_ideas', response_model=List[Idea])
async def get_liked_ideas(current_user: AuthenticatedUser = Depends(get_current_user)) -> List[Idea]:
    result = []
    relations = await USERIDEARELATIONS.get_all_relations_by_user_id(user_id=current_user.id,
                                                                     relation=UserIdeaRelations.like)
    for relation in relations:
        result.append(await IDEA.get_by_id(relation.idea_id))
    return result


@router.get('/disliked_ideas', response_model=List[Idea])
async def get_disliked_ideas(current_user: AuthenticatedUser = Depends(get_current_user)) -> List[Idea]:
    result = []
    relations = await USERIDEARELATIONS.get_all_relations_by_user_id(user_id=current_user.id,
                                                                     relation=UserIdeaRelations.dislike)
    for relation in relations:
        result.append(await IDEA.get_by_id(relation.idea_id))
    return result
