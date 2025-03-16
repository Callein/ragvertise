from typing import List

from pydantic import BaseModel

from schema.generate_dto import GenerateDTO
from schema.search_dto import SearchDTO


class RankDTO:
    class GetRankPtfoReqDTO(BaseModel):
        user_prompt: str

        def to_summary_req_dto(self) -> GenerateDTO.SummaryReqDTO:
            return GenerateDTO.SummaryReqDTO(
                user_prompt=self.user_prompt,
            )

    class GetRankPtfoRespDTO(BaseModel):
        generated: GenerateDTO.SummaryServDTO
        search_results: List[SearchDTO.PtfoSearchRespDTO]