from typing import List

from pydantic import BaseModel


class SearchDTOV2:
    class SearchRequest(BaseModel):
        desc: str
        what: str
        how: str
        style: str
        diversity: bool = False

    class SearchResponse(BaseModel):
        final_score: float
        text_score: float
        what_score: float
        how_score: float
        style_score: float
        ptfo_seqno: int
        ptfo_nm: str
        ptfo_desc: str
        tag_names: List[str]