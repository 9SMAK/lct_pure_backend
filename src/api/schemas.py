from enum import auto
from pydantic import BaseModel
from fastapi_utils.enums import CamelStrEnum


class OkResponse(BaseModel):
    result: str = 'ok'


class HomePageResponse(BaseModel):
    username: str
    message: str


class SqlReturn(BaseModel):
    username: str
    value: int


class ResponseStatus(CamelStrEnum):
    ok = auto()
    error = auto()
