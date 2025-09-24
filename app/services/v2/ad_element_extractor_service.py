# SPDX-License-Identifier: Apache-2.0

import time
import json
import re
import logging
from typing import Optional, Tuple

from app.core.config import ModelConfig
from app.schemas.v2.ad_element_extractor_dto import AdElementDTOV2
from app.utils.gemini_api import GeminiClient           # 내부에 rate limit 포함
from app.utils.ollama_api import OllamaClient           # 별도 모듈로 분리
from app.utils.log_utils import get_logger

logger = get_logger("AdElementExtractorServiceV2")


class AdElementExtractorServiceV2:
    """
    LLM(provider=gemini/ollama)으로 desc/what/how/style 추출.
    - Gemini의 RPM 제한은 GeminiClient 내부에서 처리 → 여기서는 재시도만 관리.
    - Ollama는 리미트 없음.
    - 동일 인터페이스(chat_completion(system_prompt, user_prompt)) 사용.
    """

    MAX_RETRIES: int = int(getattr(ModelConfig, "LLM_MAX_RETRIES", 3))

    SYSTEM_PROMPT = (
        "너는 광고 전문가야. 사용자 입력으로부터 아래 4가지를 추출해줘:\n"
        "1) desc (유저가 요청한 광고에 대한 한 문장 요약/설명만. 브랜드명이나 특정 제품명은 포함하지마!)\n"
        "2) what (한 단어로, 무엇을 광고하려는지, 중분류로. 브랜드명이나 특정 제품명은 빼고, 카테고리로만 적어.)\n"
        "3) how (한 단어로, 어떤 매체/도구/방식으로 광고하는지. 브랜드명, 세부명칭 등은 제외해.)\n"
        "4) style (한 단어로, 광고의 톤/스타일. 불필요한 세부내용이나 브랜드명은 제외해.)\n\n"
        "답변은 무조건 한글만 사용해.\n"
        "브랜드명, 특정 회사명, 제품명 등은 절대 포함하지마. 아래 형식으로만 응답해:\n"
        '{"desc": "...", "what": "...", "how": "...", "style": "..."}'
    )

    def __init__(
        self,
        gemini_client: Optional[GeminiClient] = None,
        ollama_client: Optional[OllamaClient] = None,
    ):
        # 같은 인스턴스 재사용 (gemini의 경우 RPM 관리해야 하므로)
        self._gemini = gemini_client or GeminiClient()
        self._ollama = ollama_client or OllamaClient(model=getattr(ModelConfig, "OLLAMA_MODEL", None))


    def extract_elements(self, req: AdElementDTOV2.AdElementRequest) -> AdElementDTOV2.AdElementResponse:
        provider, _model = self._get_provider_and_model()

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                start_time = time.time()
                if provider == "gemini":
                    response_text = self._gemini.chat_completion(self.SYSTEM_PROMPT, req.user_prompt)
                elif provider == "ollama":
                    response_text = self._ollama.chat_completion(self.SYSTEM_PROMPT, req.user_prompt)
                else:
                    raise RuntimeError(f"Unsupported provider: {provider}")

                elapsed = (time.time() - start_time) * 1000
                logger.info(f"[LLM {provider}] time={elapsed:.2f}ms")

                logger.info(f"[LLM {provider}] attempt={attempt}, response={response_text}")

                parsed = self._extract_json_from_response(response_text or "")
                if parsed:
                    return AdElementDTOV2.AdElementResponse(
                        desc=parsed.get("desc", ""),
                        what=parsed.get("what", ""),
                        how=parsed.get("how", ""),
                        style=parsed.get("style", "")
                    )

                raise ValueError("LLM 응답 파싱 실패: JSON 객체를 추출하지 못했습니다.")

            except Exception as e:
                logger.warning(f"[LLM {provider}] extract_elements 실패 (attempt {attempt}/{self.MAX_RETRIES}): {e}")
                if attempt == self.MAX_RETRIES:
                    logger.error("최대 재시도 초과. 빈 값으로 반환합니다.")
                    return AdElementDTOV2.AdElementResponse(desc="", what="", how="", style="")


    @staticmethod
    def _get_provider_and_model() -> Tuple[str, Optional[str]]:
        provider = (getattr(ModelConfig, "LLM_PROVIDER", "") or "").lower()
        if provider == "ollama":
            return "ollama", getattr(ModelConfig, "OLLAMA_MODEL", None)
        if provider == "gemini":
            return "gemini", getattr(ModelConfig, "GEMINI_MODEL", None)
        logger.warning(f"Unknown LLM_PROVIDER='{provider}', fallback to 'gemini'")
        return "gemini", getattr(ModelConfig, "GEMINI_MODEL", None)

    @staticmethod
    def _extract_json_from_response(response_text: str) -> dict | None:
        """
        LLM 응답에서 JSON 객체만 추출.
        - 코드블록(```` ``` ) 안에 있으면 내용만 꺼냄.
        """
        try:
            if "```" in response_text:
                code_blocks = re.findall(r"```(?:json)?(.*?)```", response_text, re.DOTALL)
                if code_blocks:
                    response_text = code_blocks[0].strip()
            parsed = json.loads(response_text)
            return parsed if isinstance(parsed, dict) else None
        except Exception as e:
            logger.warning(f"JSON 파싱 실패: {e}")
            return None


# 싱글톤
ad_element_extractor_service_single_ton = AdElementExtractorServiceV2()