from app.core.config import RankConfig
from app.preprocess.text_cleaner import TextCleaner
from app.schemas.v2.ad_element_extractor_dto import AdElementDTOV2
from app.schemas.v3.rank_dto import RankDTOV3
from app.schemas.v3.search_dto import SearchDTOV3
from app.services.v2.ad_element_extractor_service import ad_element_extractor_service_single_ton
from app.services.v3.search_service import search_service_singleton
from app.utils.log_utils import get_logger

logger = get_logger("RankServiceV3")


class RankServiceV3:
    """
    광고 랭킹 서비스 (V3).
    - factor 추출 → 검색 서비스 호출 → 랭킹 + 스튜디오 TOP 집계 포함 응답
    """

    DEFAULT_LIMIT = 5
    MAX_LIMIT = 50

    def __init__(self):
        self.search_service = search_service_singleton
        self.cleaner = TextCleaner()

    def get_ranked_portfolios(self, req: RankDTOV3.GetRankPtfoRequest) -> RankDTOV3.GetRankPtfoResponse:
        """
        사용자 프롬프트로 요소 추출 → 랭킹 + 스튜디오 TOP 반환
        """
        ad_element_req = req.to_ad_element_req_dto()
        ad_element_resp = ad_element_extractor_service_single_ton.extract_elements(ad_element_req)

        limit = self._validate_limit(getattr(req, "limit", None))
        min_cands = RankConfig.MIN_CANDIDATE_TOP_STDO_K
        top_studio_k = RankConfig.TOP_STDO_K

        return self._rank_with_ad_elements(
            ad_element_resp,
            limit=limit,
            diversity=getattr(req, "diversity", False),
            min_candidates=min_cands,
            top_studio_k=top_studio_k,
        )

    def get_ranked_portfolios_by_ad_elements(
        self, req: RankDTOV3.GetRankPtfoByAdElementsRequest
    ) -> RankDTOV3.GetRankPtfoResponse:
        """
        이미 추출된 요소로 랭킹 + 스튜디오 TOP 반환
        """
        ad_elements = req.to_ad_element_resp_dto()
        limit = self._validate_limit(req.limit)
        min_cands = RankConfig.MIN_CANDIDATE_TOP_STDO_K
        top_studio_k = RankConfig.TOP_STDO_K

        return self._rank_with_ad_elements(
            ad_elements,
            limit=limit,
            diversity=req.diversity,
            min_candidates=min_cands,
            top_studio_k=top_studio_k,
        )

    def _validate_limit(self, limit: int | None) -> int:
        """
        limit 값 유효성 검사 및 기본/최대 제한
        """
        if not isinstance(limit, int) or limit <= 0:
            logger.warning(f"[RankServiceV3] 잘못된 limit 값({limit}) → 기본값 {self.DEFAULT_LIMIT} 적용")
            return self.DEFAULT_LIMIT
        if limit > self.MAX_LIMIT:
            logger.warning(f"[RankServiceV3] limit({limit})이 최대값 초과 → {self.MAX_LIMIT}으로 제한")
            return self.MAX_LIMIT
        return limit

    def _rank_with_ad_elements(
        self,
        ad_element_resp: AdElementDTOV2.AdElementResponse,
        *,
        limit: int,
        diversity: bool,
        min_candidates: int,
        top_studio_k: int,
    ) -> RankDTOV3.GetRankPtfoResponse:
        """
        광고 요소 기반 검색 + 스튜디오 TOP 집계 포함 반환
        """
        full_text = self._build_full_text(ad_element_resp)
        clean_full_text = self.cleaner.clean(full_text)

        search_req = SearchDTOV3.SearchRequest(
            full=clean_full_text,
            desc=ad_element_resp.desc,
            what=ad_element_resp.what,
            how=ad_element_resp.how,
            style=ad_element_resp.style,
            limit=limit,
            diversity=diversity,
        )

        results, extra = self.search_service.search(
            search_req,
            min_candidates=min_candidates,
            want_studio_stats=True,
            top_studio_k=top_studio_k,
        )

        return RankDTOV3.GetRankPtfoResponse(
            generated=ad_element_resp,
            search_results=results,
            top_studios=extra.get("studio_stats", []),
            candidate_size=extra.get("candidate_size", len(results)),
        )

    @staticmethod
    def _build_full_text(ad_elements: AdElementDTOV2.AdElementResponse) -> str:
        """
        광고 요소를 하나의 전체 문장 문자열로 조합

        Args:
            ad_elements (AdElementDTOV2.AdElementResponse): 광고 요소 (desc, what, how, style)

        Returns:
            str: 조합된 광고 요소 문장 (예: "desc: ... what: ... how: ... style: ...")
        """
        return (
            f"desc: {ad_elements.desc}. "
            f"what: {ad_elements.what}. "
            f"how: {ad_elements.how}. "
            f"style: {ad_elements.style}"
        )