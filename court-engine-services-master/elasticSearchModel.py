from pydantic import BaseModel


class SearchModel(BaseModel):
    queryText: str
    fromYear: str
    toYear: str
    respondent: list
    petitioner: list
    section: list
    text_sections: list
    court: list = []
    highCourtLocation: str = ""
    JudgementNumber: str = ""
