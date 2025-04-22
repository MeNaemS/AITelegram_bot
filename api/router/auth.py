from fastapi import APIRouter, Depends
from typing import Annotated
from models.verify import Token
from dependences.auth import auth_login, auth_register

router: APIRouter = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(token: Annotated[Token, Depends(auth_login)]) -> Token:
    return token


@router.post("/register", response_model=Token)
async def register(token: Annotated[Token, Depends(auth_register)]) -> Token:
    return token
