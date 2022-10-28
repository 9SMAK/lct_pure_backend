import uuid
import aiofiles
from fastapi import Request, Response
from fastapi import Header


from fastapi import APIRouter, Depends, UploadFile, Body, File, HTTPException, status, Path
from starlette.responses import StreamingResponse, FileResponse
from starlette.templating import Jinja2Templates

from src.config import UserIdeaRelations, FILES_PATH
from src.api.schemas import OkResponse
from src.api.utils import create_dir, async_upload_file, read_from_file
from src.database.repositories import IDEA, USERIDEARELATIONS
from src.api.auth.authentication import AuthenticatedUser, get_current_user
from src.api.idea.schemas import CreateIdeaRequest, IdeaIdRequest

router = APIRouter(prefix="/idea", tags=["Idea"])
templates = Jinja2Templates(directory="templates")
CHUNK_SIZE = 1024 * 1024


@router.post("/create")
async def create_idea(*,
                      current_user: AuthenticatedUser = Depends(get_current_user),
                      photo: UploadFile = File(...),
                      video: UploadFile = None,
                      info: CreateIdeaRequest = Body(...)) -> OkResponse:
    project_directory_id = str(uuid.uuid4())
    photo_id = str(uuid.uuid4())
    video_id = str(uuid.uuid4())

    idea = await IDEA.add(
        title=info.title,
        description=info.description,
        author=current_user.id,
        likes=0,
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


@router.post("/like")
async def like_idea(*,
                    current_user: AuthenticatedUser = Depends(get_current_user),
                    idea_id: int) -> OkResponse:
    like_exist = await USERIDEARELATIONS.get_by_user_id(user_id=current_user.id,
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
    dislike_exist = await USERIDEARELATIONS.get_by_user_id(user_id=current_user.id,
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


@router.get("/get_all_ideas")
async def get_all_ideas():
    result = await IDEA.get_all()
    return result


@router.get("/get_idea_by_id")
async def get_idea_by_id(idea_id: int):
    result = await IDEA.get_by_id(idea_id)
    return result


@router.get("/video")
async def video_endpoint(idea_id: int):
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


@router.get("/photo")
async def photo_endpoint(idea_id: int):
    idea_info = await IDEA.get_by_id(idea_id)

    if not idea_info:
        raise HTTPException(detail="Idea not found.", status_code=status.HTTP_404_NOT_FOUND)

    return FileResponse(f'{FILES_PATH}{idea_info.project_directory_id}/{idea_info.photo_id}.jpg')
