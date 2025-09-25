# SPDX-License-Identifier: Apache-2.0
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

from app.api.v1.router import api_v1_router
from app.api.v2.router import api_v2_router
from app.api.v3.router import api_v3_router
from app.core.config import EnvVariables

# .env 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(title="RAGvertise API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(api_v2_router, prefix="/api/v2")
app.include_router(api_v3_router, prefix="/api/v3")

@app.get("/")
def root():
    return {"message": "Welcome to RAGvertise API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(EnvVariables.API_PORT))