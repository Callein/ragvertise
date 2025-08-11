from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

from app.schemas.v3.production_example_dto import ProductionExampleDTOV3 as DTO
from app.services.v3.ad_production_example_service import AdProductionExampleServiceV3

router = APIRouter()
_service = AdProductionExampleServiceV3()

@router.post("/generate", response_model=DTO.ProductionExampleResponse)
async def generate_production_example(req: DTO.ProductionExampleRequest):
    try:
        # 동기 서비스 → threadpool로 오프로딩
        return await run_in_threadpool(_service.generate, req)
    except Exception as e:
        # 429/Quota 메시지 등 그대로 전달
        raise HTTPException(status_code=429 if "한도" in str(e) else 500, detail=str(e)) from e