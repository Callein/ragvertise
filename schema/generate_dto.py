from typing import List, Dict, Any

from pydantic import BaseModel

from schema.search_dto import SearchDTO


class GenerateDTO:
    class SummaryReqDTO(BaseModel):
        user_prompt: str

    class SummaryServDTO(BaseModel):
        summary: str
        tags: List[str]

        def to_ptfo_search_req_dto(self) -> SearchDTO.PtfoSearchReqDTO:
            return SearchDTO.PtfoSearchReqDTO(
                summary=self.summary,
                tags=self.tags,
            )
