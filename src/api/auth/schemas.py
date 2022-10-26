from pydantic import BaseModel


class RegistrationData(BaseModel):
    login: str
    password: str


class LoginResponse(BaseModel):
    user_id: int
    access_token: str
    token_type: str = "bearer"
