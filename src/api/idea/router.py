import uuid
from typing import List

from fastapi import APIRouter, Depends, UploadFile, Body, File, HTTPException, status
from starlette.responses import StreamingResponse, FileResponse

from src.config import UserIdeaRelations, FILES_PATH
from src.api.schemas import OkResponse
from src.api.helpers import create_dir, async_upload_file, read_from_file, remove_file
from src.database.repositories import IDEA, USERIDEARELATIONS, COMMENT
from src.api.auth.authentication import AuthenticatedUser, get_current_user
from src.api.idea.schemas import CreateIdeaRequest, EditIdeaRequest, CommentRequest
from src.database.schemas import Idea, Comment

router = APIRouter(prefix="/idea", tags=["Idea"])


# TODO: add author to members
@router.post("/create", response_model=OkResponse)
async def create_idea(*,
                      current_user: AuthenticatedUser = Depends(get_current_user),
                      logo: UploadFile,
                      photos: List[UploadFile] = None,
                      video: UploadFile = None,
                      info: CreateIdeaRequest = Body(...)) -> OkResponse:
    logo_id = str(uuid.uuid4())
    video_id = str(uuid.uuid4()) if video else None
    photos = [(str(uuid.uuid4()), photo) for photo in photos]

    idea = await IDEA.add(
        title=info.title,
        description=info.description,
        author=current_user.id,
        likes_count=0,
        comments_count=0,
        logo_id=logo_id,
        photo_ids=[id for id, _ in photos],
        video_id=video_id,
        approved=False
    )

    if not idea:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Проект с таким именем существует",
        )

    await async_upload_file(file=logo,
                            file_id=logo_id,
                            ext='.jpg')

    for id, photo in photos:
        await async_upload_file(file=photo,
                                file_id=id,
                                ext='.jpg')

    if video:
        await async_upload_file(file=video,
                                file_id=video_id,
                                ext='.mp4')

    return OkResponse()


@router.post("/edit", response_model=OkResponse)
async def edit_idea(*,
                    current_user: AuthenticatedUser = Depends(get_current_user),
                    id: int,
                    logo: UploadFile = None,
                    photos: List[UploadFile] = None,
                    video: UploadFile = None,
                    info: EditIdeaRequest = Body(...)) -> OkResponse:
    idea = await IDEA.get_by_id(id)
    photos = [(str(uuid.uuid4()), photo) for photo in photos]

    if not idea.author == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="It is not your idea",
        )

    if logo:
        await remove_file(f'{idea.logo_id}.jpg')
        await async_upload_file(file=logo,
                                file_id=idea.logo_id,
                                ext='.jpg')

    if photos:
        for prev_photo in idea.photo_ids:
            await remove_file(f'{prev_photo}.jpg')

        for id, photo in photos:
            await async_upload_file(file=photo,
                                    file_id=id,
                                    ext='.jpg')
        photo_id_info = {"photo_ids": [id for id, photo in photos]}
        await IDEA.edit_idea(idea.id, **photo_id_info)

    if video:
        if idea.video_id:
            await remove_file(f'{idea.video_id}.mp4')

        video_id = str(uuid.uuid4()) if not idea.video_id else idea.video_id

        if not idea.video_id:
            video_id_info = {"video_id": video_id}
            await IDEA.edit_idea(idea.id, **video_id_info)

        await async_upload_file(file=video,
                                file_id=video_id,
                                ext='.mp4')

    res = await IDEA.edit_idea(idea.id, **info.dict(exclude_none=True))

    if not res:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while modifying base",
        )

    return OkResponse()


@router.post("/like", response_model=OkResponse)
async def like_idea(*,
                    current_user: AuthenticatedUser = Depends(get_current_user),
                    id: int) -> OkResponse:
    like_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=current_user.id,
                                                                 idea_id=id,
                                                                 relation=UserIdeaRelations.like)

    if like_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Like exist",
        )

    relation = await USERIDEARELATIONS.add(
        user_id=current_user.id,
        idea_id=id,
        relation=UserIdeaRelations.like
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
                                                                    relation=UserIdeaRelations.dislike)
    if dislike_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Like exist",
        )

    relation = await USERIDEARELATIONS.add(
        user_id=current_user.id,
        idea_id=id,
        relation=UserIdeaRelations.dislike
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
                                                                    relation=UserIdeaRelations.request_membership)
    member_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=current_user.id,
                                                                   idea_id=id,
                                                                   relation=UserIdeaRelations.member)

    if request_exist or member_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already in team or sent request",
        )

    relation = await USERIDEARELATIONS.add(
        user_id=current_user.id,
        idea_id=id,
        relation=UserIdeaRelations.request_membership
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


@router.get("/get_all_ideas", response_model=List[Idea])
async def get_all_ideas() -> List[Idea]:
    result = await IDEA.get_all()
    return result


@router.get("/get_approved_ideas", response_model=List[Idea])
async def get_approved_ideas() -> List[Idea]:
    result = await IDEA.get_approved()
    return result


@router.get("/get_my_ideas", response_model=List[Idea])
async def get_idea_by_id(*,
                         current_user: AuthenticatedUser = Depends(get_current_user)) -> List[Idea]:
    result = await IDEA.get_my_ideas(current_user.id)
    return result


@router.get("/get_idea_by_id", response_model=Idea)
async def get_idea_by_id(id: int) -> Idea:
    result = await IDEA.get_by_id(id)
    return result


@router.get("/get_unwatched_idea", response_model=List[Idea])
async def get_unwatched_ideas(*,
                              current_user: AuthenticatedUser = Depends(get_current_user)) -> List[Idea]:
    all_ideas = await IDEA.get_approved()
    all_relations = await USERIDEARELATIONS.get_all_by_user_id(user_id=current_user.id)
    all_relations_ids = [relation.idea_id for relation in all_relations]
    result = [idea for idea in all_ideas if idea.id not in all_relations_ids]

    if len(result) == 0:
        raise HTTPException(detail="No ideas to show.", status_code=status.HTTP_404_NOT_FOUND)

    return result[0]
