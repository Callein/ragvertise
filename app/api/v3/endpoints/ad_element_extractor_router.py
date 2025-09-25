# SPDX-License-Identifier: Apache-2.0
from fastapi import APIRouter, HTTPException
from app.schemas.v2.ad_element_extractor_dto import AdElementDTOV2
from app.services.v2.ad_element_extractor_service import AdElementExtractorServiceV2

router = APIRouter()

@router.post("/extract", response_model=AdElementDTOV2.AdElementResponse)
async def extract_ad_elements(req: AdElementDTOV2.AdElementRequest):
    try:
        ad_element_extractor_service_v2 = AdElementExtractorServiceV2()
        return ad_element_extractor_service_v2.extract_elements(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))