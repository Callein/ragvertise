from typing import List, Optional
from pydantic import BaseModel


class StudioStat(BaseModel):
    name: str
    count: int
    ratio: float

class Generated(BaseModel):
    desc: str
    what: str
    how: str
    style: str

class SearchResult(BaseModel):
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
    view_lnk_url: Optional[str] = None
    prdn_stdo_nm: Optional[str] = None
    prdn_cost: Optional[float] = None
    prdn_perd: Optional[str] = None


class ProductionExampleDTOV3:
    # Rank 응답을 그대로 받는 요청
    class ProductionExampleRequest(BaseModel):
        generated: Generated
        search_results: List[SearchResult]
        top_studios: List[StudioStat] = []
        candidate_size: int

    class ProductionExampleResponse(BaseModel):
        example: str