from app.preprocess.text_cleaner import TextCleaner
from app.schemas.v2.ad_element_extractor_dto import AdElementDTOV2
from app.schemas.v2.rank_dto import RankDTOV2
from app.schemas.v2.search_dto import SearchDTOV2
from app.services.v2.ad_element_extractor_service import ad_element_extractor_service_single_ton
from app.services.v2.search_service import SearchServiceV2


class RankServiceV2:
    """
    광고 랭킹 서비스 (V2).

    - 사용자의 입력 데이터를 바탕으로 factor (desc, what, how, style) 를 추출
    - 검색 서비스를 통해 포트폴리오 랭킹 결과 반환
    """

    def __init__(self):
        self.search_service = SearchServiceV2()
        self.cleaner = TextCleaner()

    def get_ranked_portfolios(self, req: RankDTOV2.GetRankPtfoRequest) -> RankDTOV2.GetRankPtfoResponse:
        """
        주어진 요청(req)을 기반으로 광고 포트폴리오를 순위별로 반환.

        Args:
            req (RankDTOV2.GetRankPtfoRequest): 사용자의 요청 데이터

        Returns:
            RankDTOV2.GetRankPtfoResponse: factor (desc, what, how, style) 및 랭킹 결과
        """
        ad_element_req = req.to_ad_element_req_dto()
        ad_element_resp = ad_element_extractor_service_single_ton.extract_elements(ad_element_req)

        return self._rank_with_ad_elements(ad_element_resp, req.diversity)

    def get_ranked_portfolios_by_ad_elements(self, req: RankDTOV2.GetRankPtfoByAdElementsRequest) -> RankDTOV2.GetRankPtfoResponse:
        """
        이미 추출된 광고 요소(ad_elements)를 기반으로 유사도 검사를 수행하고
        관련된 포트폴리오를 랭킹 순서로 반환합니다.

        Args:
            req (RankDTOV2.GetRankPtfoByAdElementsRequest): 광고 요소 및 diversity 옵션이 포함된 요청 객체

        Returns:
            RankDTOV2.GetRankPtfoResponse: 생성된 광고 요소와 랭킹된 포트폴리오 리스트
        """
        ad_elements = req.to_ad_element_resp_dto()
        return self._rank_with_ad_elements(ad_elements, req.diversity)

    def _rank_with_ad_elements(
            self,
            ad_element_resp: AdElementDTOV2.AdElementResponse,
            diversity: int
    ) -> RankDTOV2.GetRankPtfoResponse:
        """
        광고 요소(ad_element_resp)를 기반으로 포트폴리오를 검색하고 랭킹 결과를 반환합니다.

        Args:
            ad_element_resp (RankDTOV2.AdElementResponse): 광고 요소 정보 (desc, what, how, style)
            diversity (int): 검색 결과 다양성 조정 값

        Returns:
            RankDTOV2.GetRankPtfoResponse: 광고 요소와 해당 요소 기반의 포트폴리오 랭킹 결과
        """
        full_text = self._build_full_text(ad_element_resp)
        clean_full_text = self.cleaner.clean(full_text)

        search_req = SearchDTOV2.SearchRequest(
            full=clean_full_text,
            desc=ad_element_resp.desc,
            what=ad_element_resp.what,
            how=ad_element_resp.how,
            style=ad_element_resp.style,
            diversity=diversity
        )

        search_results = self.search_service.search(request=search_req)

        return RankDTOV2.GetRankPtfoResponse(
            generated=ad_element_resp,
            search_results=search_results
        )

    @staticmethod
    def _build_full_text(ad_elements: AdElementDTOV2.AdElementResponse) -> str:
        """
        광고 요소를 하나의 전체 문장 문자열로 조합합니다.

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