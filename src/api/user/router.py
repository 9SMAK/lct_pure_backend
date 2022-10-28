from fastapi import APIRouter, Depends, HTTPException, status

from src.database.repositories import USERIDEARELATIONS, IDEA, USER
from src.api.auth.authentication import AuthenticatedUser, get_current_user
from src.config import UserIdeaRelations
from src.api.user.schemas import EditProfileRequest

router = APIRouter(prefix="/user", tags=["User"])


@router.post('/edit_profile')
async def get_liked_ideas(*, current_user: AuthenticatedUser = Depends(get_current_user), edit_info: EditProfileRequest):
    result = await USER.edit_profile(current_user.id, **edit_info.dict(exclude_none=True))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while editing profile",
        )
    return edit_info


@router.get('/liked_ideas')
async def get_liked_ideas(current_user: AuthenticatedUser = Depends(get_current_user)):
    result = []
    relations = await USERIDEARELATIONS.get_by_user_id(user_id=current_user.id, relation=UserIdeaRelations.like)
    for relation in relations:
        result.append(await IDEA.get_by_id(relation.idea_id))
    return result


@router.get('/disliked_ideas')
async def get_disliked_ideas(current_user: AuthenticatedUser = Depends(get_current_user)):
    result = []
    relations = await USERIDEARELATIONS.get_by_user_id(user_id=current_user.id, relation=UserIdeaRelations.dislike)
    for relation in relations:
        result.append(await IDEA.get_by_id(relation.idea_id))
    return result
