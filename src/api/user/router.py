from fastapi import APIRouter, Depends


from src.database.repositories import USERIDEARELATIONS, IDEA
from src.api.auth.authentication import AuthenticatedUser, get_current_user
from src.config import UserIdeaRelations

router = APIRouter(prefix="/user", tags=["User"])


@router.get('/liked')
async def get_liked_ideas(current_user: AuthenticatedUser = Depends(get_current_user)):
    result = []
    relations = await USERIDEARELATIONS.get_by_user_id(user_id=current_user.id, relation=UserIdeaRelations.like)
    for relation in relations:
        result.append(await IDEA.get_by_id(relation.idea_id))
    return result


@router.get('/disliked')
async def get_disliked_ideas(current_user: AuthenticatedUser = Depends(get_current_user)):
    result = []
    relations = await USERIDEARELATIONS.get_by_user_id(user_id=current_user.id, relation=UserIdeaRelations.dislike)
    for relation in relations:
        result.append(await IDEA.get_by_id(relation.idea_id))
    return result
