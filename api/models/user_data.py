from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class UserAuth(BaseModel):
    login: str
    password: str


class UserInToken(BaseModel):
    username: str
    id: int


class UserOptionalInfo(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    patronymic: Optional[str] = None


class UserRegister(UserAuth, UserOptionalInfo):
    email: Optional[str] = None


class UserInDB(UserAuth, UserOptionalInfo):
    id: int
    created_at: datetime
