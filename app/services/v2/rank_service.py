from app.preprocess.text_cleaner import TextCleaner
from app.schemas.v2.rank_dto import RankDTOV2
from app.schemas.v2.search_dto import SearchDTOV2
from app.services.v2.ad_element_extractor_service import ad_element_extractor_service_single_ton
from app.services.v2.search_service import SearchServiceV2


class RankServiceV2:
    """
    광고 랭킹 서비스 (V2).

    - 사용자의 입력 데이터를 바탕으로 광고 요소를 추출
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
            RankDTOV2.GetRankPtfoResponse: 광고 요소 및 랭킹된 결과
        """
        ad_element_req = req.to_ad_element_req_dto()
        ad_element_resp = ad_element_extractor_service_single_ton.extract_elements(ad_element_req)

        full_text = f"desc: {ad_element_resp.desc}. what: {ad_element_resp.what}. how: {ad_element_resp.how}. style: {ad_element_resp.style}"
        clean_full_text = self.cleaner.clean(full_text)

        search_req = SearchDTOV2.SearchRequest(
            full=clean_full_text,
            desc=ad_element_resp.desc,
            what=ad_element_resp.what,
            how=ad_element_resp.how,
            style=ad_element_resp.style,
            diversity=req.diversity
        )

        search_results = self.search_service.search(request=search_req)

        return RankDTOV2.GetRankPtfoResponse(
            generated=ad_element_resp,
            search_results=search_results
        )