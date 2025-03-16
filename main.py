from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router.generate_router import generate_router
from router.healthcheck_router import healthcheck_router
from constant.env_variables import EnvVariables
from dotenv import load_dotenv

from router.rank_router import rank_router
from router.test_router import test_api_router

# .env 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(root_path="/api")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(healthcheck_router, prefix="/healthcheck")
app.include_router(test_api_router, prefix="/test")
app.include_router(generate_router, prefix="/generate")
app.include_router(rank_router, prefix="/rank")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(EnvVariables.API_PORT))