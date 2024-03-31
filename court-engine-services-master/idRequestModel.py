from pydantic import BaseModel


class IdRequestModel(BaseModel):
    id: str
