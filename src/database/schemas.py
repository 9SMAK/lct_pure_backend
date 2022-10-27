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
    project_directory_id: str
    photo_id: str
    video_id: str = None

    class Config:
        orm_mode = True
