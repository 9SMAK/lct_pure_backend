from typing import List, Dict
from pydantic import BaseModel, Field


class UserAuthData(BaseModel):
    name: str
    password: str