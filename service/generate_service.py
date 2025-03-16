import json

import ollama

from schema.generate_dto import GenerateDTO


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
        persona: 너는 유저의 광고 요청을 정리해주는 최고의 AI비서야.
        instruction:
             - 모든 답은 한국어로.
             - 답변 방식은 JSON 형식으로.
        JSON 필드:
            tags: 입력된 텍스트에서 광고 카테고리 추출. 
            summary: 키워드 위주로 요약.
        태그종류:
            홍보영상,행사 스케치,TV CF,관공서,앱/서비스,식음료,공간/인테리어,교육/기관,자동차,뷰티,의료/제약,음악/리드미컬,기록/정보전달,코믹/흥미유발,공감형성,신뢰형성,브랜딩,모션/인포그래픽,드론,배우/모델,숏폼,3D,제품/기술
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.user_prompt}
        ]
        llm_resp  = ollama.chat(model="mistral", messages=messages)

        try:
            llm_data = json.loads(llm_resp["message"]["content"])
        except Exception as e:
            raise Exception("LLM 응답 파싱 실패: " + str(e))

        tags = llm_data.get("tags", [])
        summary = llm_data.get("summary", "")

        return GenerateDTO.SummaryServDTO(
            summary=summary,
            tags=tags
        )
