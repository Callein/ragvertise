import ollama

from app.schemas.v1.generate_dto import GenerateDTO
from app.utils.json_extractor import extract_json_from_response


class GenerateService:
    @staticmethod
    def generate_summary(request: GenerateDTO.SummaryReqDTO) -> GenerateDTO.SummaryServDTO:
        """
            사용자가 광고 촬영에 대해 자유롭게 입력한 텍스트를 기반으로 LLM(mistral 모델)을 호출하여,
            광고 요청을 정리한 JSON 결과를 얻습니다.
            이 JSON 결과는 "tags"와 "summary" 필드를 포함하며, 이를 통해 SearchService에 전달할 DTO를 생성합니다.

        동작 과정:
            1. 시스템 프롬프트 정의

            2. 메시지 구성 및 LLM 호출:
                - 시스템 프롬프트와 사용자 입력(request.user_prompt)을 포함하는 메시지 리스트를 구성합니다.
                - ollama.chat()을 호출하여 LLM(mistral 모델)에 요청을 보냅니다.

            3. LLM 응답 처리 및 JSON 파싱:
                - LLM 응답에서 "message" 필드의 "content" 값을 추출합니다.
                - 이 값은 JSON 형식의 문자열로, json.loads()를 통해 파싱하여 딕셔너리로 변환합니다.
                - 파싱 실패 시 적절한 예외를 발생시킵니다.

            4. 결과 추출 및 DTO 생성:
                - 파싱된 딕셔너리에서 "tags"와 "summary" 값을 추출합니다.
                - 추출한 값을 이용해 GenerateDTO.SummaryServDTO 객체를 생성하여 반환합니다.

        반환값:
            GenerateDTO.SummaryServDTO 객체로, LLM이 생성한 요약(summary)과 태그(tags)를 포함합니다.
        """

        system_prompt = """
        너는 입력된 광고 요청 문장을 분석하여 JSON 형식의 결과만 출력하는 시스템이야.

        🔒 주의사항:
        - 출력은 반드시 JSON만! (다른 텍스트, 설명, 문장은 절대 포함하지 마)
        - 예시:
          {
            "tags": [],
            "summary": ""
          }

        필수 필드:
        - tags: 광고 관련 태그 리스트 (반드시 태그 목록에서만 선택)
        - summary: 한 문장 요약 (핵심 키워드 중심, 한국어로 작성)

        태그 목록:
        ["홍보영상", "행사 스케치", "TV CF", "관공서", "앱/서비스", "식음료", "공간/인테리어", "교육/기관" ,"자동차", "뷰티", "의료/제약", "음악/리드미컬", "기록/정보전달", "코믹/흥미유발", "공감형성", "신뢰형성", "브랜딩", "모션/인포그래픽", "드론", "배우/모델", "숏폼", "3D", "제품/기술"]
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.user_prompt}
        ]
        llm_resp  = ollama.chat(model="llama3:8b", messages=messages)
        llm_response_str = llm_resp["message"]["content"]
        print(llm_response_str)

        llm_data = extract_json_from_response(llm_response_str)

        tags = llm_data.get("tags", [])
        summary = llm_data.get("summary", "")

        return GenerateDTO.SummaryServDTO(
            summary=summary,
            tags=tags
        )
