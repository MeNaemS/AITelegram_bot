from typing import TypedDict, Optional


class UserInToken(TypedDict):
    id: int
    username: str


class UserInDB(TypedDict):
    id: int
    login: str
    password: str
    email: str
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
