import json
from typing import List
from pydantic import BaseModel

from src.database.schemas import User, Idea
from src.api.user.schemas import ShortUser


class CreateIdeaRequest(BaseModel):
    title: str
    description: str

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class EditIdeaRequest(BaseModel):
    title: str = None
    description: str = None

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


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
