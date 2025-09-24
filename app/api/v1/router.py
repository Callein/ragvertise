# SPDX-License-Identifier: Apache-2.0
from fastapi import APIRouter


from app.api.v1.endpoints.generate_router import generate_router
from app.api.v1.endpoints.rank_router import rank_router
from app.api.v1.endpoints.test_router  import test_router
from app.api.v1.endpoints.healthcheck_router import healthcheck_router

api_v1_router = APIRouter()

api_v1_router.include_router(test_router, prefix="/test", tags=["Test"])
api_v1_router.include_router(healthcheck_router, prefix="/healthcheck", tags=["Healthcheck"])
api_v1_router.include_router(generate_router, prefix="/generate", tags=["Generate"])
api_v1_router.include_router(rank_router, prefix="/rank", tags=["Rank"])
