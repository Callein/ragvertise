from fastapi import APIRouter, HTTPException

from schema.generate_dto import GenerateDTO
from service.generate_service import GenerateService

generate_router = APIRouter()

@generate_router.post("/summary")
async def generate_summary(request: GenerateDTO.SummaryReqDTO):
    try:
        return GenerateService.generate_summary(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))