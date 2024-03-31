from pydantic import BaseModel


class SearchQueryModel(BaseModel):
    queryString: str
