from typing import List, Optional

from pydantic import BaseModel

from app.schemas.generate_dto import GenerateDTO
from app.schemas.search_dto import SearchDTO


class RankDTO:
    class GetRankPtfoReqDTO(BaseModel):
        user_prompt: str
        diversity: Optional[bool] = False

        def to_summary_req_dto(self) -> GenerateDTO.SummaryReqDTO:
            return GenerateDTO.SummaryReqDTO(
                user_prompt=self.user_prompt,
            )

    class GetRankPtfoRespDTO(BaseModel):
        generated: GenerateDTO.SummaryServDTO
        search_results: List[SearchDTO.PtfoSearchRespDTO]