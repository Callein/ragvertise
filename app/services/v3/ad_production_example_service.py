# SPDX-License-Identifier: Apache-2.0

import json
import logging
import time
from typing import Optional

from app.schemas.v3.production_example_dto import ProductionExampleDTOV3 as DTO
from app.utils.gemini_api import GeminiClient
from app.utils.log_utils import get_logger

logger = get_logger("AdProductionExampleServiceV3")


class AdProductionExampleServiceV3:
    """
    Rank 응답을 받아 광고 작업지시서 예시를 생성.
    - GeminiClient 내부에 RPM 관리 포함.
    - 429/Quota 초과 시 메시지 구분 처리.
    """
    MAX_RETRIES = 3

    def __init__(self, gemini: Optional[GeminiClient] = None):
        self.gemini = gemini or GeminiClient()

    def generate(self, req: DTO.ProductionExampleRequest) -> DTO.ProductionExampleResponse:
        system_prompt, user_prompt = self._build_prompt(req)

        last_err = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                text = self.gemini.chat_completion(system_prompt, user_prompt)
                if not text or not text.strip():
                    raise RuntimeError("빈 응답")
                return DTO.ProductionExampleResponse(example=text.strip())
            except Exception as e:
                msg = str(e)
                last_err = e
                logger.warning(f"[AdProductionExample] attempt={attempt} failed: {msg}")

                # Gemini 429 / quota 초과 메시지 감지
                if "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower() or "429" in msg:
                    # 재시도 보류: 사용량 소진은 빠른 재시도 의미 없음
                    raise RuntimeError(
                        "일일 무료 한도를 초과했어요. 잠시 후 다시 시도하거나 유료 키/한도를 확인해 주세요."
                    ) from e

                if attempt < self.MAX_RETRIES:
                    time.sleep(1.5 * attempt)  # 점진적 backoff
                else:
                    raise RuntimeError("작업지시서 생성에 실패했어요. 잠시 후 다시 시도해 주세요.") from last_err

        # 여기는 도달하지 않음
        return DTO.ProductionExampleResponse(example="")

    @staticmethod
    def _build_prompt(req: DTO.ProductionExampleRequest) -> tuple[str, str]:
        """
        - system: 역할/톤/출력 포맷 정의
        - user: Rank 결과(생성요소/검색결과/스튜디오 통계)를 JSON으로 전달
        """
        system_prompt = (
            "너는 상업영상 제작 전문 프로듀서야. 사용자가 제공한 '광고 요소'와 '유사 포트폴리오', "
            "'상위 스튜디오 통계'를 참고해서 실무에서 바로 쓰는 '광고 작업지시서 예시'를 한국어로 작성해.\n"
            "- 전문적이되 간결하고 실무자(감독/PD/촬영/편집/클라이언트)가 바로 이해할 수 있게.\n"
            "- 너무 추상적이지 말고, 실제 촬영/편집/일정/인력/산출물 기준으로 구체화.\n"
            "- 불필요한 수사는 피하고, 항목형으로 깔끔하게 정리.\n"
            "- 예산은 추정하지 말고, 기간도 과장 없이 합리적인 범위 제시.\n"
            "- 특정 브랜드/고유명사는 입력 데이터에 있을 때만 그대로 사용.\n"
            "- 출력은 Markdown 섹션으로:\n"
            "  1) 프로젝트 개요\n"
            "  2) 목표/핵심 메시지\n"
            "  3) 타깃 및 톤앤매너\n"
            "  4) 레퍼런스 요약(입력 포트폴리오 기반 핵심 포인트)\n"
            "  5) 콘셉트 및 장면 구성(숏리스트 수준)\n"
            "  6) 제작 방식(촬영/장비/로케/출연/아트/사운드)\n"
            "  7) 편집/그래픽/모션 가이드\n"
            "  8) 산출물 스펙(해상도/비율/길이/버전)\n"
            "  9) 일정(프리프로/촬영/후반)\n"
            "  10) 리스크/의사결정 포인트\n"
            "  11) 추가 제안(선택)\n"
        )

        # 필요한 핵심 필드만 요약: JSON으로 안전 전달
        compact = {
            "generated": req.generated.dict(),
            "top_studios": [s.dict() for s in req.top_studios],
            "candidate_size": req.candidate_size,
            "search_results": [
                {
                    "ptfo_nm": r.ptfo_nm,
                    "ptfo_desc": r.ptfo_desc,
                    "tags": r.tags,
                    "view_lnk_url": r.view_lnk_url,
                    "prdn_stdo_nm": r.prdn_stdo_nm,
                    "prdn_perd": r.prdn_perd,
                    # 점수는 요약용으로 핵심만
                    "scores": {
                        "final": r.final_score,
                        "full": r.full_score,
                        "desc": r.desc_score,
                        "what": r.what_score,
                        "how": r.how_score,
                        "style": r.style_score,
                    },
                    # 요소 텍스트
                    "factors": {
                        "desc": r.desc,
                        "what": r.what,
                        "how": r.how,
                        "style": r.style,
                    },
                }
                for r in req.search_results[:8]  # 프롬프트 과다 길이 방지 (최대 8개)
            ],
        }
        user_prompt = json.dumps(compact, ensure_ascii=False, indent=2)
        return system_prompt, user_prompt