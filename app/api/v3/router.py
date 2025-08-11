from fastapi import APIRouter
from app.api.v3.endpoints import ad_element_extractor_router, rank_router, production_example_router

api_v3_router = APIRouter()

# 광고 요소 추출 API
api_v3_router.include_router(ad_element_extractor_router.router, prefix="/ad-element", tags=["ad-element"])

# 순위화된 포트폴리오 검색 API
api_v3_router.include_router(rank_router.router, prefix="/rank", tags=["rank"])

api_v3_router.include_router(production_example_router.router, prefix="/production_example", tags=["v3"])