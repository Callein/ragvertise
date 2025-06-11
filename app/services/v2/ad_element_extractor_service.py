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
            "너는 광고 전문가야. 사용자 입력으로부터 아래 4가지를 추출해줘:\n"
            "1) desc (유저가 요청한 광고에 대한 한 문장 요약/설명만. 브랜드명이나 특정 제품명은 포함하지마!)\n"
            "2) what (한 단어로, 무엇을 광고하려는지, 중분류로. 브랜드명이나 특정 제품명은 빼고, 카테고리로만 적어.)\n"
            "3) how (한 단어로, 어떤 매체/도구/방식으로 광고하는지. 브랜드명, 세부명칭 등은 제외해.)\n"
            "4) style (한 단어로, 광고의 톤/스타일. 불필요한 세부내용이나 브랜드명은 제외해.)\n\n"
            "브랜드명, 특정 회사명, 제품명 등은 절대 포함하지마. 아래 형식으로만 응답해:\n"
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

ad_element_extractor_service_single_ton = AdElementExtractorServiceV2()