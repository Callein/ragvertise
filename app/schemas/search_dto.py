from pydantic import BaseModel


class SearchDTO:
    class PtfoSearchReqDTO(BaseModel):
        summary: str
        tags: list
        diversity: bool

    class PtfoSearchRespDTO(BaseModel):
        final_score: float
        text_score: float
        tag_score: float
        ptfo_seqno: int
        ptfo_nm: str
        ptfo_desc: str
        tag_names: list