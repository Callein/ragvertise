import os
import logging
import time
from datetime import datetime, timedelta, UTC

from google import genai
from google.genai import types

from app.core.config import ModelConfig

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        """
        Gemini API Key 로 client 초기화 및 rate limit 관리.
        """
        self.client = genai.Client(api_key=ModelConfig.GEMINI_API_KEY)
        self.request_count = 0
        self.request_window_start = datetime.now(UTC)
        self.max_requests_per_minute = int(ModelConfig.GEMINI_API_REQUESTS_PER_MINUTE)

    def enforce_rate_limit(self):
        """
        1분당 15회 호출 제한을 초과하면 대기
        """
        now = datetime.now(UTC)
        if (now - self.request_window_start) > timedelta(minutes=1):
            # 1분 지났으면 카운터 초기화
            self.request_count = 0
            self.request_window_start = now

        if self.request_count >= self.max_requests_per_minute:
            # 대기시간 계산 후 대기
            wait_seconds = 60 - (now - self.request_window_start).seconds
            logger.info(f"[GeminiClient] 요청 {self.max_requests_per_minute}회 초과. {wait_seconds}초 대기합니다...")
            time.sleep(wait_seconds)
            # 초기화
            self.request_count = 0
            self.request_window_start = datetime.now(UTC)

    def chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        """
        system + user prompt 기반 Gemini 호출 + 요청 제한 로직 반영
        """
        self.enforce_rate_limit()
        try:
            response = self.client.models.generate_content(
                model= ModelConfig.GEMINI_MODEL,
                config=types.GenerateContentConfig(system_instruction=system_prompt),
                contents=user_prompt,
            )
            self.request_count += 1  # 호출 성공 시 count 증가
            return response.text.strip()
        except Exception as e:
            logger.error(f"[GeminiClient] Gemini API 호출 실패: {e}")
            raise Exception(f"[GeminiClient] Gemini API 호출 실패: {e}") from e