# SPDX-License-Identifier: Apache-2.0
from fastapi import APIRouter

healthcheck_router = APIRouter()

@healthcheck_router.get("")
async def healthcheck():
    return {"status": "API is running"}
