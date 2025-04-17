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
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]


class UserRegister(UserAuth, UserOptionalInfo):
    email: str


class UserInDB(UserAuth, UserOptionalInfo):
    id: int
    created_at: datetime
