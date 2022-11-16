import json
from typing import List
from pydantic import BaseModel

from src.database.schemas import User, Idea
from src.api.user.schemas import ShortUser


class CreateIdeaRequest(BaseModel):
    title: str
    description: str


class CreateIdeaResponse(BaseModel):
    id: int


class EditIdeaRequest(BaseModel):
    title: str = None
    description: str = None


class IdeaResponse(Idea):
    author: ShortUser
    members: List[User]


class TeamRequest(BaseModel):
    idea: Idea
    requests: List[User]


class CommentRequest(BaseModel):
    idea_id: int
    reply_comment_id: int = None
    text: str
