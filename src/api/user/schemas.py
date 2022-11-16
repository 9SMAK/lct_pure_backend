import datetime
import json

from pydantic import BaseModel


class EditProfileRequest(BaseModel):
    login: str = None
    name: str = None
    birth: datetime.date = None
    email: str = None
    phone: str = None
    telegram: str = None
    github: str = None


class EditSkillsRequest(BaseModel):
    id: int
    weight: int


class User(BaseModel):
    id: int
    login: str
    is_admin: bool
    avatar_id: str = None
    name: str = None
    birth: datetime.date = None
    email: str = None
    phone: str = None
    telegram: str = None
    github: str = None

    class Config:
        orm_mode = True


class ShortUser(BaseModel):
    id: int
    login: str
    avatar_id: str = None

    class Config:
        orm_mode = True
