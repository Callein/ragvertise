import json, re

from app.core.config import ModelConfig
from app.schemas.v2.ad_element_extractor_dto import AdElementDTOV2
from app.utils.gemini_api import GeminiClient
from app.utils.log_utils import get_logger

logger = get_logger("AdElementExtractorServiceV2")


class AdElementExtractorServiceV2:
    MAX_RETRIES = int(ModelConfig.GEMINI_API_REQUESTS_PER_MINUTE)

    @staticmethod
    def extract_elements(req: AdElementDTOV2.AdElementRequest) -> AdElementDTOV2.AdElementResponse:
        system_prompt = (
            "너는 광고 전문가야. 사용자 입력으로부터 아래 3가지를 추출해줘:\n"
            "1) desc (유저가 요청한 광고에 대한 설명)"
            "2) what (무엇을 광고하려는지)\n"
            "3) how (어떤 매체/도구/방식으로 광고하는지)\n"
            "4) style (광고의 톤/스타일)\n\n"
            "아래 형식으로만 응답해줘 (JSON):\n"
            '{"desc": "...", "what": "...", "how": "...", "style": "..."}'
        )

        gemini = GeminiClient()
        response_text = None

        for attempt in range(1, AdElementExtractorServiceV2.MAX_RETRIES + 1):
            response_text = gemini.chat_completion(system_prompt, req.user_prompt)
            logger.info(f"[Gemini 응답] {response_text}")

            # JSON 파싱 시도
            parsed = AdElementExtractorServiceV2._extract_json_from_response(response_text)
            if parsed:
                return AdElementDTOV2.AdElementResponse(
                    desc=parsed.get("desc", ""),
                    what=parsed.get("what", ""),
                    how=parsed.get("how", ""),
                    style=parsed.get("style", "")
                )
            else:
                logger.warning(f"Gemini 응답 파싱 실패 - {attempt}차 시도")

        # 모든 시도 실패 시 기본 빈 값 반환
        logger.warning("Gemini 응답 파싱 실패 - 기본 빈 값 반환")
        return AdElementDTOV2.AdElementResponse(desc="", what="", how="", style="")

    @staticmethod
    def _extract_json_from_response(response_text: str) -> dict | None:
        """
        마크다운 코드 블록이나 불필요한 텍스트를 제거하고 JSON만 추출.
        :param response_text: LLM이 반환한 원본 응답
        :return: JSON dict or None
        """
        try:
            # 마크다운 코드 블록 제거 (```json ... ```)
            if "```" in response_text:
                code_blocks = re.findall(r"```(?:json)?(.*?)```", response_text, re.DOTALL)
                if code_blocks:
                    response_text = code_blocks[0].strip()

            # JSON 파싱
            parsed = json.loads(response_text)
            if isinstance(parsed, dict):
                return parsed
            else:
                return None
        except Exception as e:
            logger.warning(f"JSON 파싱 실패: {e}")
            return None