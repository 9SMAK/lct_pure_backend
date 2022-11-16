import uuid
from typing import List

from fastapi import APIRouter, Depends, UploadFile, Body, File, HTTPException, status
from src.config import RelationsTypes, FILES_PATH
from src.api.schemas import OkResponse
from src.api.helpers import create_dir, async_upload_file, remove_file
from src.database.repositories import IDEA, USERIDEARELATIONS, COMMENT, USER, TAGTOIDEA
from src.api.auth.authentication import AuthenticatedUser, get_current_user
from src.api.idea.schemas import CreateIdeaRequest, EditIdeaRequest, CommentRequest, IdeaResponse, CreateIdeaResponse
from src.api.user.schemas import User, ShortUser, EditSkillsRequest
from src.database.schemas import Idea, Comment

router = APIRouter(prefix="/idea", tags=["Idea"])


async def convert_to_req_idea(idea: Idea):
    user = await USER.get_by_id(id=idea.author_id)
    members = await USERIDEARELATIONS.get_all_members(idea_id=idea.id)
    members = [await USER.get_by_id(id=member.user_id) for member in members]
    return IdeaResponse(**idea.dict(), author=ShortUser(**user.dict()), members=members)


@router.post("/create", response_model=CreateIdeaResponse)
async def create_idea(*,
                      current_user: AuthenticatedUser = Depends(get_current_user),
                      info: CreateIdeaRequest) -> CreateIdeaResponse:
    idea = await IDEA.add(
        title=info.title,
        description=info.description,
        author_id=current_user.id,
        likes_count=0,
        comments_count=0,
        logo_id=None,
        photo_ids=None,
        video_id=None,
        approved=False
    )

    if not idea:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with same name exists",
        )

    # idea = await IDEA.get_idea_by_title(title=info.title)
    return CreateIdeaResponse(id=idea)


@router.post("/edit_idea_logo", response_model=OkResponse)
async def edit_idea_logo(*,
                         current_user: AuthenticatedUser = Depends(get_current_user),
                         id: int,
                         logo: UploadFile) -> OkResponse:
    logo_id = str(uuid.uuid4())

    idea = await IDEA.get_by_id(id=id)
    if idea.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="It is not your idea",
        )

    await async_upload_file(file=logo,
                            file_id=logo_id,
                            ext='.jpg')

    await IDEA.edit_idea(idea_id=id, **{"logo_id": logo_id})
    return OkResponse()


@router.post("/edit_idea_photos", response_model=OkResponse)
async def edit_idea_photos(*,
                           current_user: AuthenticatedUser = Depends(get_current_user),
                           id: int,
                           photos: List[UploadFile]) -> OkResponse:
    photos = [(str(uuid.uuid4()), photo) for photo in photos]
    idea = await IDEA.get_by_id(id=id)
    if idea.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="It is not your idea",
        )

    for ph_id, photo in photos:
        await async_upload_file(file=photo,
                                file_id=id,
                                ext='.jpg')

    await IDEA.edit_idea(idea_id=id, **{"photo_ids": [ph_id for ph_id, _ in photos]})
    return OkResponse()


@router.post("/edit_idea_video", response_model=OkResponse)
async def edit_idea_video(*,
                          current_user: AuthenticatedUser = Depends(get_current_user),
                          id: int,
                          video: UploadFile) -> OkResponse:
    video_id = str(uuid.uuid4())

    idea = await IDEA.get_by_id(id=id)
    if idea.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="It is not your idea",
        )

    await async_upload_file(file=video,
                            file_id=video_id,
                            ext='.mp4')

    await IDEA.edit_idea(idea_id=id, **{"video_id": video_id})
    return OkResponse()


@router.post("/edit", response_model=OkResponse)
async def edit_idea(*,
                    current_user: AuthenticatedUser = Depends(get_current_user),
                    id: int,
                    info: EditIdeaRequest = Body(...)) -> OkResponse:
    idea = await IDEA.get_by_id(id)

    if not idea.author_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="It is not your idea",
        )

    res = await IDEA.edit_idea(idea.id, **info.dict(exclude_none=True))

    if not res:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while modifying base",
        )

    return OkResponse()


@router.post('/edit_tags', response_model=OkResponse)
async def edit_tags(*, current_user: AuthenticatedUser = Depends(get_current_user),
                    idea_id: int,
                    weights: List[EditSkillsRequest]) -> OkResponse:
    idea = await IDEA.get_by_id(idea_id)

    if not idea.author_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="It is not your idea",
        )

    for skill in weights:
        result = await TAGTOIDEA.add(
            tag_id=int(skill.id),
            idea_id=idea_id,
            weight=skill.weight
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error while editing profile",
            )
    return OkResponse()


@router.post("/like", response_model=OkResponse)
async def like_idea(*,
                    current_user: AuthenticatedUser = Depends(get_current_user),
                    id: int) -> OkResponse:
    like_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=current_user.id,
                                                                 idea_id=id,
                                                                 relation=RelationsTypes.like)

    if like_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Like exist",
        )

    relation = await USERIDEARELATIONS.add(
        user_id=current_user.id,
        idea_id=id,
        relation=RelationsTypes.like
    )

    await IDEA.safe_increase_like(
        idea_id=id
    )

    if not relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while modifying base",
        )

    return OkResponse()


@router.post("/dislike", response_model=OkResponse)
async def dislike_idea(*,
                       current_user: AuthenticatedUser = Depends(get_current_user),
                       id: int) -> OkResponse:
    dislike_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=current_user.id,
                                                                    idea_id=id,
                                                                    relation=RelationsTypes.dislike)
    if dislike_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Like exist",
        )

    relation = await USERIDEARELATIONS.add(
        user_id=current_user.id,
        idea_id=id,
        relation=RelationsTypes.dislike
    )

    if not relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while modifying base",
        )

    return OkResponse()


@router.post("/request_membership", response_model=OkResponse)
async def request_membership(*,
                             current_user: AuthenticatedUser = Depends(get_current_user),
                             id: int) -> OkResponse:
    request_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=current_user.id,
                                                                    idea_id=id,
                                                                    relation=RelationsTypes.request_membership)
    member_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=current_user.id,
                                                                   idea_id=id,
                                                                   relation=RelationsTypes.member)

    if request_exist or member_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already in team or sent request",
        )

    relation = await USERIDEARELATIONS.add(
        user_id=current_user.id,
        idea_id=id,
        relation=RelationsTypes.request_membership
    )

    if not relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while modifying base",
        )

    return OkResponse()


@router.post("/comment", response_model=OkResponse)
async def comment_idea(*,
                       current_user: AuthenticatedUser = Depends(get_current_user),
                       comment: CommentRequest) -> OkResponse:
    await IDEA.safe_increase_comments(idea_id=comment.idea_id)
    res = await COMMENT.add(
        idea_id=comment.idea_id,
        user_id=current_user.id,
        reply_comment_id=comment.reply_comment_id,
        text=comment.text
    )

    if not res:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while modifying base",
        )

    return OkResponse()


@router.get("/get_comments_by_id", response_model=List[Comment])
async def get_comments_by_id(id: int) -> Comment:
    result = await COMMENT.get_comments_by_id(idea_id=id)
    return result


@router.get("/get_all_ideas", response_model=List[IdeaResponse])
async def get_all_ideas() -> List[IdeaResponse]:
    ideas = await IDEA.get_all()
    result = [await convert_to_req_idea(idea) for idea in ideas]
    return result


@router.get("/get_approved_ideas", response_model=List[IdeaResponse])
async def get_approved_ideas() -> List[IdeaResponse]:
    ideas = await IDEA.get_approved()
    result = [await convert_to_req_idea(idea) for idea in ideas]
    return result


@router.get("/get_my_ideas", response_model=List[IdeaResponse])
async def get_my_ideas(*,
                       current_user: AuthenticatedUser = Depends(get_current_user)) -> List[IdeaResponse]:
    ideas = await IDEA.get_my_ideas(current_user.id)
    result = [await convert_to_req_idea(idea) for idea in ideas]
    return result


@router.get("/get_idea_by_id", response_model=IdeaResponse)
async def get_idea_by_id(id: int) -> IdeaResponse:
    idea = await IDEA.get_by_id(id)
    result = await convert_to_req_idea(idea)
    return result


@router.get("/get_unwatched_idea", response_model=IdeaResponse)
async def get_unwatched_ideas(*,
                              current_user: AuthenticatedUser = Depends(get_current_user)) -> IdeaResponse:
    ideas = await IDEA.get_approved()
    relations = await USERIDEARELATIONS.get_all_by_user_id(user_id=current_user.id)
    relations_ids = [relation.idea_id for relation in relations]
    result = [idea for idea in ideas if idea.id not in relations_ids]

    if len(result) == 0:
        raise HTTPException(detail="No ideas to show", status_code=status.HTTP_400_BAD_REQUEST)

    idea = await convert_to_req_idea(result[0])

    return idea
