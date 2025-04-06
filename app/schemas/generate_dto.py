from typing import List

from pydantic import BaseModel

from app.schemas.search_dto import SearchDTO


class GenerateDTO:
    class SummaryReqDTO(BaseModel):
        user_prompt: str

    class SummaryServDTO(BaseModel):
        summary: str
        tags: List[str]

        def to_ptfo_search_req_dto(self, diversity) -> SearchDTO.PtfoSearchReqDTO:
            return SearchDTO.PtfoSearchReqDTO(
                summary=self.summary,
                tags=self.tags,
                diversity=diversity,
            )
