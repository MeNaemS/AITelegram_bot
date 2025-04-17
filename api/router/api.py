from typing import Annotated
from fastapi import APIRouter, Depends
from dependences.bot_request import depends_ask_bot
from models.openrouterai.integration import Response

router: APIRouter = APIRouter(prefix="/api", tags=["api"])


@router.post("/ask_bot", response_model=Response)
async def ask_bot(response: Annotated[Response, Depends(depends_ask_bot)]) -> Response:
    return response
