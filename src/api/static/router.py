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

router = APIRouter(prefix="/static", tags=["Static"])


@router.get("/video_stream")
async def video_stream_endpoint(file_id: str) -> StreamingResponse:
    try:
        file_contents = read_from_file(
            file_id=file_id,
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
async def video_endpoint(file_id: str) -> FileResponse:
    return FileResponse(f'{FILES_PATH}{file_id}.mp4')


@router.get("/photo")
async def photo_endpoint(file_id: str) -> FileResponse:
    return FileResponse(f'{FILES_PATH}{file_id}.jpg')
