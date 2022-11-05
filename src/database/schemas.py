import datetime
from typing import List

from src.api.user.schemas import User
from pydantic import BaseModel


class UserDB(User):
    hashed_password: str


class Idea(BaseModel):
    id: int
    title: str
    description: str
    author_id: int
    likes_count: int
    comments_count: int
    logo_id: str
    photo_ids: List
    video_id: str = None
    approved: bool = False

    class Config:
        orm_mode = True


class UserIdeaRelations(BaseModel):
    id: int
    user_id: int
    idea_id: int
    relation: int

    class Config:
        orm_mode = True


class Comment(BaseModel):
    id: int
    user_id: int
    idea_id: int
    reply_comment_id: int = None
    text: str

    class Config:
        orm_mode = True


class Skill(BaseModel):
    id: int
    name: str
    circle_id: str

    class Config:
        orm_mode = True


class IdeaTag(BaseModel):
    id: int
    name: str
    circle_id: str

    class Config:
        orm_mode = True


class SkillToUser(BaseModel):
    id: int
    user_id: int
    skill_id: int
    weight: int

    class Config:
        orm_mode = True


class IdeaTagToIdea(BaseModel):
    id: int
    idea_id: int
    tag_id: int
    weight: int

    class Config:
        orm_mode = True
