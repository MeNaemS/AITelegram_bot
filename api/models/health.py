from pydantic import BaseModel


class Health(BaseModel):
    message: str
