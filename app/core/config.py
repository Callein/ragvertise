import os
from dotenv import load_dotenv

load_dotenv()

class EnvVariables:
    API_PORT = os.getenv('API_PORT')

    # DB
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_CLASSNAME = os.getenv("DB_CLASSNAME")
    DB_PORT = os.getenv("DB_PORT")

    @staticmethod
    def get_routes_by_prefix(prefix):
        """주어진 prefix로 시작하는 .env 값을 배열로 반환."""
        routes = []
        for key, value in os.environ.items():
            if key.startswith(prefix):
                routes.append(value)
        return routes

    @staticmethod
    def get_routes_by_postfix(postfix):
        """주어진 postfix로 끝나는 .env 값을 배열로 반환."""
        routes = []
        for key, value in os.environ.items():
            if key.endswith(postfix):
                routes.append(value)
        return routes

class ModelConfig:
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    WORD_EMBEDDING_MODEL_PATH = os.getenv("WORD_EMBEDDING_MODEL_PATH")

    LLM_PROVIDER = os.getenv("LLM_PROVIDER")

    HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

    GEMINI_MODEL = os.getenv("GEMINI_MODEL")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_API_URL = os.getenv("GEMINI_API_URL")
    GEMINI_API_REQUESTS_PER_MINUTE = os.getenv("GEMINI_API_REQUESTS_PER_MINUTE")


class SearchConfig:
    ALPHA = float(os.getenv("SEARCH_ALPHA", 0.5))
    BETA = float(os.getenv("SEARCH_BETA", 0.5))
    TAG_TOP_K = int(os.getenv("TAG_TOP_K", 3))
    TAG_SIM_THRESHOLD = float(os.getenv("TAG_SIM_THRESHOLD", 0.5))
    TAG_PENALTY_FACTOR = float(os.getenv("TAG_PENALTY_FACTOR", 3.0))
    FULL_WEIGHT = float(os.getenv("FULL_WEIGHT", 1.0))
    DESC_WEIGHT = float(os.getenv("DESC_WEIGHT", 1.0))
    WHAT_WEIGHT = float(os.getenv("WHAT_WEIGHT", 1.0))
    HOW_WEIGHT = float(os.getenv("HOW_WEIGHT", 1.0))
    STYLE_WEIGHT = float(os.getenv("STYLE_WEIGHT", 1.0))

class RankConfig:
    MIN_CANDIDATE_TOP_STDO = int(os.getenv("MIN_CANDIDATE_TOP_STDO", 30))
    TOP_STDO_K = int(os.getenv("TOP_STDO_K", 5))
