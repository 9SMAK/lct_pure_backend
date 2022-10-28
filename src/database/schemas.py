import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
    login: str
    hashed_password: str
    is_admin: bool
    first_name: str = None
    last_name: str = None
    birth: datetime.date = None
    email: str = None
    phone: str = None
    telegram: str = None
    github: str = None

    class Config:
        orm_mode = True


class Idea(BaseModel):
    id: int
    title: str
    description: str
    author: int
    likes_count: int
    comments_count: int
    project_directory_id: str
    photo_id: str
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
