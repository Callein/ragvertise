from typing import List

from pydantic import BaseModel


class SearchDTOV2:
    class SearchRequest(BaseModel):
        full: str
        desc: str
        what: str
        how: str
        style: str
        limit: int
        diversity: bool = False

    class SearchResponse(BaseModel):
        final_score: float
        full_score: float
        desc_score: float
        what_score: float
        how_score: float
        style_score: float
        desc: str
        what: str
        how: str
        style: str
        ptfo_seqno: int
        ptfo_nm: str
        ptfo_desc: str
        tags: List[str]