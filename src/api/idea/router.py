import uuid
from typing import List

from fastapi import APIRouter, Depends, UploadFile, Body, File, HTTPException, status
from starlette.responses import StreamingResponse, FileResponse

from src.config import UserIdeaRelations, FILES_PATH
from src.api.schemas import OkResponse
from src.api.utils import create_dir, async_upload_file, read_from_file, remove_file
from src.database.repositories import IDEA, USERIDEARELATIONS, COMMENT
from src.api.auth.authentication import AuthenticatedUser, get_current_user
from src.api.idea.schemas import CreateIdeaRequest, EditIdeaRequest, CommentRequest
from src.database.schemas import Idea, Comment

router = APIRouter(prefix="/idea", tags=["Idea"])


# TODO: add author to members
@router.post("/create")
async def create_idea(*,
                      current_user: AuthenticatedUser = Depends(get_current_user),
                      photo: UploadFile = File(...),
                      video: UploadFile = None,
                      info: CreateIdeaRequest = Body(...)) -> OkResponse:
    project_directory_id = str(uuid.uuid4())
    photo_id = str(uuid.uuid4())
    video_id = str(uuid.uuid4()) if video else None

    idea = await IDEA.add(
        title=info.title,
        description=info.description,
        author=current_user.id,
        likes_count=0,
        comments_count=0,
        project_directory_id=project_directory_id,
        photo_id=photo_id,
        video_id=video_id,
        approved=False
    )

    if not idea:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Проект с таким именем существует",
        )

    await create_dir(project_directory_id)
    await async_upload_file(file=photo,
                            project_directory_id=project_directory_id,
                            file_id=photo_id,
                            ext='.jpg')

    if video:
        await async_upload_file(file=video,
                                project_directory_id=project_directory_id,
                                file_id=video_id,
                                ext='.mp4')

    return OkResponse()


@router.post("/edit")
async def edit_idea(*,
                    current_user: AuthenticatedUser = Depends(get_current_user),
                    idea_id: int,
                    photo: UploadFile = None,
                    video: UploadFile = None,
                    info: EditIdeaRequest = Body(...)) -> OkResponse:
    idea = await IDEA.get_by_id(idea_id)

    if not idea.author == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="It is not your idea",
        )

    if photo:
        await remove_file(idea.project_directory_id, f'{idea.photo_id}.jpg')
        await async_upload_file(file=photo,
                                project_directory_id=idea.project_directory_id,
                                file_id=idea.photo_id,
                                ext='.jpg')

    if video:
        if idea.video_id:
            await remove_file(idea.project_directory_id, f'{idea.video_id}.mp4')

        video_id = str(uuid.uuid4()) if not idea.video_id else idea.video_id

        if not idea.video_id:
            video_id_info = {"video_id": video_id}
            await IDEA.edit_idea(idea_id, **video_id_info)

        await async_upload_file(file=video,
                                project_directory_id=idea.project_directory_id,
                                file_id=video_id,
                                ext='.mp4')

    res = await IDEA.edit_idea(idea_id, **info.dict(exclude_none=True))

    if not res:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while modifying base",
        )

    return OkResponse()


@router.post("/like")
async def like_idea(*,
                    current_user: AuthenticatedUser = Depends(get_current_user),
                    idea_id: int) -> OkResponse:
    like_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=current_user.id,
                                                                 idea_id=idea_id,
                                                                 relation=UserIdeaRelations.like)

    if like_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Like exist",
        )

    relation = await USERIDEARELATIONS.add(
        user_id=current_user.id,
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
                       current_user: AuthenticatedUser = Depends(get_current_user),
                       idea_id: int) -> OkResponse:
    dislike_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=current_user.id,
                                                                    idea_id=idea_id,
                                                                    relation=UserIdeaRelations.dislike)
    if dislike_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Like exist",
        )

    relation = await USERIDEARELATIONS.add(
        user_id=current_user.id,
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
                             current_user: AuthenticatedUser = Depends(get_current_user),
                             idea_id: int) -> OkResponse:
    request_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=current_user.id,
                                                                    idea_id=idea_id,
                                                                    relation=UserIdeaRelations.request_membership)
    member_exist = await USERIDEARELATIONS.get_relation_by_user_id(user_id=current_user.id,
                                                                   idea_id=idea_id,
                                                                   relation=UserIdeaRelations.member)

    if request_exist or member_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already in team or sent request",
        )

    relation = await USERIDEARELATIONS.add(
        user_id=current_user.id,
        idea_id=idea_id,
        relation=UserIdeaRelations.request_membership
    )

    if not relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while modifying base",
        )

    return OkResponse()


@router.post("/comment")
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


@router.get("/get_comments_by_id")
async def get_comments_by_id(idea_id: int) -> Comment:
    result = await COMMENT.get_comments_by_id(idea_id=idea_id)
    return result


@router.get("/get_all_ideas")
async def get_all_ideas() -> List[Idea]:
    result = await IDEA.get_all()
    return result


@router.get("/get_approved_ideas")
async def get_approved_ideas() -> List[Idea]:
    result = await IDEA.get_approved()
    return result


@router.get("/get_my_ideas")
async def get_idea_by_id(*,
                         current_user: AuthenticatedUser = Depends(get_current_user)) -> List[Idea]:
    result = await IDEA.get_my_ideas(current_user.id)
    return result


@router.get("/get_idea_by_id")
async def get_idea_by_id(idea_id: int) -> Idea:
    result = await IDEA.get_by_id(idea_id)
    return result


@router.get("/get_unwatched_ideas")
async def get_unwatched_ideas(*,
                              current_user: AuthenticatedUser = Depends(get_current_user)) -> List[Idea]:
    all_ideas = await IDEA.get_approved()
    all_relations = await USERIDEARELATIONS.get_all_by_user_id(user_id=current_user.id)
    all_relations_ids = [relation.idea_id for relation in all_relations]
    result = [idea for idea in all_ideas if idea.id not in all_relations_ids]

    return result


@router.get("/video_stream")
async def video_stream_endpoint(idea_id: int) -> StreamingResponse:
    idea_info = await IDEA.get_by_id(idea_id)
    try:
        file_contents = read_from_file(project_directory_id=idea_info.project_directory_id,
                                       file_id=idea_info.video_id,
                                       ext='.mp4')
        response = StreamingResponse(
            content=file_contents,
            status_code=status.HTTP_200_OK,
            media_type="video/mp4",
        )
        return response
    except FileNotFoundError:
        raise HTTPException(detail="File not found.", status_code=status.HTTP_404_NOT_FOUND)


@router.get("/video")
async def video_endpoint(idea_id: int) -> FileResponse:
    idea_info = await IDEA.get_by_id(idea_id)

    if not idea_info:
        raise HTTPException(detail="Idea not found.", status_code=status.HTTP_404_NOT_FOUND)

    return FileResponse(f'{FILES_PATH}{idea_info.project_directory_id}/{idea_info.video_id}.mp4')


@router.get("/photo")
async def photo_endpoint(idea_id: int) -> FileResponse:
    idea_info = await IDEA.get_by_id(idea_id)

    if not idea_info:
        raise HTTPException(detail="Idea not found.", status_code=status.HTTP_404_NOT_FOUND)

    return FileResponse(f'{FILES_PATH}{idea_info.project_directory_id}/{idea_info.photo_id}.jpg')
