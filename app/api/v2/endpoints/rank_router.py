from fastapi import APIRouter, HTTPException
from app.schemas.v2.rank_dto import RankDTOV2
from app.services.v2.rank_service import RankServiceV2

router = APIRouter()

@router.post("/portfolios", response_model=RankDTOV2.GetRankPtfoResponse)
async def get_ranked_portfolios(req: RankDTOV2.GetRankPtfoRequest):
    try:
        rank_service = RankServiceV2()
        return rank_service.get_ranked_portfolios(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))