import uuid
import aiofiles

from fastapi import APIRouter, Depends, UploadFile, Body, File, HTTPException, status

from src.config import UserIdeaStatus
from src.api.schemas import OkResponse
from src.api.utils import create_dir, async_upload_file
from src.database.repositories import IDEA, USERIDEARELATIONS
from src.api.auth.authentication import AuthenticatedUser, get_current_user
from src.api.idea.schemas import CreateIdeaRequest, IdeaIdRequest

router = APIRouter(prefix="/idea", tags=["Idea"])


@router.post("/create")
async def create_idea(*,
                      current_user: AuthenticatedUser = Depends(get_current_user),
                      photo: UploadFile = File(...),
                      video: UploadFile = None,
                      info: CreateIdeaRequest = Body(...)) -> OkResponse:
    project_directory_id = str(uuid.uuid4()) + "/"
    photo_id = str(uuid.uuid4())
    video_id = str(uuid.uuid4())

    idea = await IDEA.add(
        title=info.title,
        description=info.description,
        author=current_user.id,
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
                            file_id=video_id,
                            ext='.jpg')

    if video:
        await async_upload_file(file=video,
                                project_directory_id=project_directory_id,
                                file_id=photo_id,
                                ext='.mp4')

    return OkResponse()


@router.post("/like")
async def like_idea(*,
                    current_user: AuthenticatedUser = Depends(get_current_user),
                    info: IdeaIdRequest) -> OkResponse:
    relation = await USERIDEARELATIONS.add(
        user_id=current_user.id,
        idea_id=info.id,
        relation=UserIdeaStatus.like
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
                       info: IdeaIdRequest) -> OkResponse:
    relation = await USERIDEARELATIONS.add(
        user_id=current_user.id,
        idea_id=info.id,
        relation=UserIdeaStatus.dislike
    )

    if not relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while modifying base",
        )

    return OkResponse()
