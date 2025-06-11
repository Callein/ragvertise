from fastapi import APIRouter
from app.api.v2.endpoints import ad_element_extractor_router, rank_router

api_v2_router = APIRouter()

# 광고 요소 추출 API
api_v2_router.include_router(ad_element_extractor_router.router, prefix="/ad-element", tags=["ad-element"])

# 순위화된 포트폴리오 검색 API
api_v2_router.include_router(rank_router.router, prefix="/rank", tags=["rank"])
