from app.schemas.v2.rank_dto import RankDTOV2
from app.schemas.v2.search_dto import SearchDTOV2
from app.services.v2.ad_element_extractor_service import AdElementExtractorServiceV2
from app.services.v2.search_service import SearchServiceV2


class RankServiceV2:
    def __init__(self):
        self.search_service = SearchServiceV2()

    def get_ranked_portfolios(self, req: RankDTOV2.GetRankPtfoRequest) -> RankDTOV2.GetRankPtfoResponse:
        ad_element_req = req.to_ad_element_req_dto()
        ad_element_resp = AdElementExtractorServiceV2.extract_elements(ad_element_req)

        search_req = SearchDTOV2.SearchRequest(
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