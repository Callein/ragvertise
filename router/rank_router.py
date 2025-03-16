from fastapi import APIRouter, HTTPException

from schema.rank_dto import RankDTO
from service.rank_service import RankService

rank_router = APIRouter()

@rank_router.post("/ptfo")
def get_rank_ptfo(request: RankDTO.GetRankPtfoReqDTO):
    try:
        return RankService.get_rank_ptfo(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
