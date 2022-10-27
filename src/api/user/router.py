from fastapi import APIRouter, Depends
from src.database.repositories import USER
from src.database.schemas import User

router = APIRouter(prefix="/user", tags=["User"])
