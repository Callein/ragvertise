from typing import List, Optional

from pydantic import BaseModel

from app.schemas.v2.ad_element_extractor_dto import AdElementDTOV2
from app.schemas.v2.search_dto import SearchDTOV2


class RankDTOV2:
    class GetRankPtfoRequest(BaseModel):
        user_prompt: str
        diversity: Optional[bool] = False
        limit: int = 5  # 보여 줄 상위 포트폴리오 개수

        def to_ad_element_req_dto(self) -> AdElementDTOV2.AdElementRequest:
            return AdElementDTOV2.AdElementRequest(
                user_prompt=self.user_prompt,
            )

    class GetRankPtfoResponse(BaseModel):
        generated: AdElementDTOV2.AdElementResponse
        search_results: List[SearchDTOV2.SearchResponse]

    class GetRankPtfoByAdElementsRequest(BaseModel):
        desc: str
        what: str
        how: str
        style: str
        limit: int = 5  # 보여 줄 상위 포트폴리오 개수
        diversity: bool = False

        def to_ad_element_resp_dto(self) -> AdElementDTOV2.AdElementResponse:
            return AdElementDTOV2.AdElementResponse(
                desc=self.desc,
                what=self.what,
                how=self.how,
                style=self.style,
            )