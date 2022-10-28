from pydantic import BaseModel


class User(BaseModel):
    id: int
    login: str
    hashed_password: str

    class Config:
        orm_mode = True


class Idea(BaseModel):
    id: int
    title: str
    description: str
    author: int
    likes: int
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
