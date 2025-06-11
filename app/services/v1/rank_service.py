from app.schemas.v1.rank_dto import RankDTO
from app.services.v1.generate_service import GenerateService
from app.services.v1.search_service import SearchService


class RankService:
    @staticmethod
    def get_rank_ptfo(request: RankDTO.GetRankPtfoReqDTO) -> RankDTO.GetRankPtfoRespDTO:
        """
        사용자의 광고 요청을 바탕으로 포트폴리오(포폴) 순위를 산출하는 기능을 수행합니다.
        이 함수는 LLM(GenerateService)을 통해 광고 요청을 요약하고, 해당 요약 정보를
        기반으로 벡터 기반 포트폴리오 검색(SearchService)을 수행하여 최종 결과를 조합하여 반환합니다.
        """

        summary_serv_dto = GenerateService.generate_summary(request.to_summary_req_dto())
        search_results = SearchService.ptfo_search(summary_serv_dto.to_ptfo_search_req_dto(request.diversity))

        return RankDTO.GetRankPtfoRespDTO(
            generated = summary_serv_dto,
            search_results = search_results,
        )