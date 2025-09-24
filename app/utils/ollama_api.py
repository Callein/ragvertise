# SPDX-License-Identifier: Apache-2.0
import logging
import ollama
from app.core.config import ModelConfig

logger = logging.getLogger(__name__)

class OllamaClient:
    """
    Ollama API 호출 래퍼
    - 모델명은 ModelConfig.OLLAMA_MODEL에서 가져옴
    - chat_completion 인터페이스 통일
    """

    def __init__(self, model: str = None):
        self.model = model or ModelConfig.OLLAMA_MODEL
        if not self.model:
            raise RuntimeError("OLLAMA_MODEL 설정이 필요합니다.")

    def chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        """
        Ollama chat API 호출
        """
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            logger.debug(f"[OllamaClient] 모델={self.model}, messages={messages}")

            resp = ollama.chat(model=self.model, messages=messages)

            return resp["message"]["content"].strip()
        except Exception as e:
            logger.error(f"[OllamaClient] API 호출 실패: {e}")
            raise RuntimeError(f"Ollama API 호출 실패: {e}") from e