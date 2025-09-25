# SPDX-License-Identifier: Apache-2.0
from fastapi import APIRouter, HTTPException

from app.schemas.v1.generate_dto import GenerateDTO
from app.services.v1.generate_service import GenerateService

generate_router = APIRouter()

@generate_router.post("/summary")
async def generate_summary(request: GenerateDTO.SummaryReqDTO):
    try:
        return GenerateService.generate_summary(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))