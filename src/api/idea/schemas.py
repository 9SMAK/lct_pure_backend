import json
from typing import List, Dict

from pydantic import BaseModel


class IdeaInfoRequest(BaseModel):
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


class IdeaInfoResponse(BaseModel):
    success: bool
    project_directory_id: str