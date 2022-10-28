import datetime
from pydantic import BaseModel


class EditProfileRequest(BaseModel):
    login: str = None
    first_name: str = None
    last_name: str = None
    birth: datetime.date = None
    email: str = None
    phone: str = None
    telegram: str = None
    github: str = None
