import json

from app.schemas.v2.ad_element_extractor_dto import AdElementDTOV2
from app.utils.gemini_api import GeminiClient
from app.utils.log_utils import get_logger

logger = get_logger("AdElementExtractorServiceV2")


class AdElementExtractorServiceV2:
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
        response = gemini.chat_completion(system_prompt, req.user_prompt)
        logger.info(f"[Gemini 응답] {response}")

        # JSON 파싱
        try:
            parsed = json.loads(response)
            return AdElementDTOV2.AdElementResponse(
                desc=parsed.get("desc", ""),
                what=parsed.get("what", ""),
                how=parsed.get("how", ""),
                style=parsed.get("style", "")
            )
        except json.JSONDecodeError:
            logger.warning("Gemini 응답 파싱 실패 - 기본 빈 값 반환")
            return AdElementDTOV2.AdElementResponse(
                desc="", what="", how="", style=""
            )