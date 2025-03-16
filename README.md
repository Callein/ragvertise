# RAGvertise Prototype

## 1️⃣ 프로젝트 개요
> 이 프로젝트는 FastAPI 기반으로 Ollama LLM (Mistral, OpenChat 3.5 등) 및 RAG 기반 검색을 활용한 광고사 추천 서비스의 프로토타입입니다.   
DB는 MariaDB를 사용하며, 벡터 검색을 위해 FAISS 또는 Qdrant를 활용할 수 있습니다.

## 2️⃣ 설치 및 초기 설정
### 📌 2.1 필수 요구사항
- Python 3.10 이상 (python --version 확인)  
- pip 및 가상환경 (venv)  
- MySQL 8.0 이상 (또는 MariaDB)  
- Ollama 설치  
- FastAPI & Uvicorn  

### 📌 2.2 프로젝트 클론 및 가상 환경 설정
```shell
# 프로젝트 클론
git clone https://github.com/Callein/ragvertise_prototype.git
cd ragvertise_prototype

# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)

# 필수 패키지 설치
pip install -r requirements.txt
```

### 📌 2.3 .env 설정 (환경 변수)
> .env 의 구성요소는 아래와 같습니다. 원본 .env 필요시 문의주세요.
```text
API_PORT=
# DB
DB_HOST=
DB_PORT=
DB_NAME=
DB_USERNAME=
DB_PASSWORD=
...
```

### 📌 2.4 Ollama 설치 및 모델 다운로드
```shell
# Ollama 설치 (Mac)
brew install --cask ollama
# Ollama 설치 (Linux)
curl -fsSL https://ollama.com/install.sh | sh

# OpenChat 3.5 모델 다운로드 (필요시에만)
ollama pull openchat:3.5

# 또는 Mistral 7B 다운로드 (가벼운 모델)
ollama pull mistral
```

## 3️⃣ FastAPI 서버 실행
```shell
# 단순 실행
python main.py
# reload 필요시
uvicorn main:app --reload --port 9000
```
Port는 `9000` 입니다.


## 4️⃣ API 사용 방법
[📜 Swagger UI (Docs)](http://localhost:9000/docs)  
[📃 Redoc (Alternative Docs)](http://localhost:9000/redoc)

### 🔹 4.1 모델 테스트 API (POST /api/test/generate)
- **Request 예시**
    ```json
    {
        "system_prompt": "persona: 너는 최고의 광고 카피를 만드는 AI야.\n instruction: 모든 답은 한국어로 해.",
        "user_prompt": "헬스케어 제품을 위한 창의적인 광고 문구를 추천해줘."
    }
    ```
    #### Request Body
    | 필드명         | 타입     | 필수 여부 | 설명               |
    |--------------|--------|---------|------------------|
    | `system_prompt` | `string` | ✅       | 모델의 역할이나 지침을 전달하는 필드 |
    | `user_prompt`   | `string` | ✅       | 실제 요청을 전달하는 필드   |
    

- **Response 예시**
    ```json
    {
        "response": "1. \"체력을 강화하는 건강한 미래를 만들어라! 다양한 헬스케어 제품으로 건강하신 것처럼!\"\n\n2. \"오늘부터 건강함의 시작, 내일부터 행복한 자신과 함께하는 헬스케어 제품입니다.\"\n\n3. \"건강을 위해 가장 중요한 것은 자신의 삶! 내 삶, 내 체력, 나만의 헬스케어 제품으로 당신이 건강하시어라.\"\n\n4. \"건강함을 선택하세요. 지금부터 겸손한 시작, 건강한 미래를 만들어내세요!\"\n\n5. \"건강에서 삶의 뿌리를 발굴해보세요! 최고의 헬스케어 제품으로 건강하신 것처럼!\"\n\n6. \"행복을 위한 기원은 건강함! 건강한 체력, 건강한 마음, 건강한 삶을 위해 최고의 헬스케어 제품으로 선택해보세요.\"\n\n7. \"건강하신 것처럼 행복하시오! 혁신적인 헬스케어 제품과 함께한 당신의 건강한 삶, 건강한 미래를 만들어내세요.\"\n\n8. \"건강함을 선택하고, 행복을 누리시오! 최고의 헬스케어 제품과 함께하여 당신이 건강하시며 행복해지세요.\"\n\n9. \"건강한 체력으로 삶을 만나보세요! 최고의 헬스케어 제품과 함께, 당신의 건강한 미래를 만들어내세요.\"\n\n10. \"건강하신 것처럼 행복하시오! 최고의 헬스케어 제품과 함께, 당신의 건강한 미래를 만들어내세요.\""
    }
    ```


- 아래와 같이 시스템 프롬프트를 작성해 특정 포멧으로 답변을 받으실 수도 있습니다.
    - Request
      ```json
        {
            "system_prompt": "persona: 너는 최고의 광고 전문가야.\n instruction: \n - 모든 답은 한국어로 해.\n- 답변 방식은 JSON 형식으로. 필드는 다음과 같다. \"tags\" : 입력된 텍스트에서 광고 관련 핵심 태그를 추출, \"summary\": 입력된 텍스트 요약",
            "user_prompt": "나는 남자 아이돌들이 춤을 추며 홍보하는 광고 스타일의 영상을 찍고 싶어 클렌징 폼을 홍보하기 위해 남자 아이돌이 춤을 추며 자리에서 뛰었을때 클랜징 폼의 거품이 나는 듯한 광고를 찍은 비슷한 광고를 추천해줘"
        }
        ```
  - Response
      ```json
      {
        "response": " {\n     \"tags\": [\"남자 아이돌\", \"춤\", \"홍보\", \"클렌징 폼\"],\n     \"summary\": \"영상에서 남자 아이돌이 춤을 추며 동시에 클랜징 폼의 거품이 나는 광고입니다. 춤과 클렌징 폼이 조합된 매력적인 모습으로 관심을 유발할 수 있을 것입니다.\"\n   }"      
      }
      ```
### 🔹 4.2 포트폴리오 랭크 리스트 생성 API (POST /api/rank/ptfo)
  > 이 API는 사용자의 광고 촬영 요청(또는 관련 아이디어)을 바탕으로 포트폴리오(광고 제작 사례) 리스트의 순위를 산출합니다.
  1. **LLM 요약 및 태그 생성**  
     - 사용자가 입력한 광고 요청 텍스트와 미리 정의된 시스템 프롬프트와 함께 LLM(현재 Mistral 모델 사용)에 요청을 보냅니다.
     - 이를 통해 광고 요청에 대한 요약(`summary`)과 관련 광고 카테고리 태그(`tags`)를 추출합니다.
     
  2. **포트폴리오 검색 및 순위 산출** 
     - **임베딩 및 유사도 계산**  
       - **임베딩 모델 초기화**  
         `SentenceTransformer('all-MiniLM-L6-v2')` 모델을 사용하여 LLM이 생성한 사용자 요청의 `summary`와 `tags`를 임베딩합니다.
       - **텍스트 유사도 계산 (FAISS 사용)**  
         - 전처리 과정에서 포트폴리오 임베딩 벡터들을 L2 정규화한 후, FAISS의 `IndexFlatIP` (내적 기반 인덱스)를 생성합니다.  
         - 사용자 입력 요약을 임베딩하고 정규화하여 전체 포트폴리오 임베딩과의 내적(코사인 유사도와 동일한 효과)을 계산합니다.  
         - 계산된 내적 값에 따라 각 포트폴리오의 텍스트 유사도 점수를 산출합니다.
       - **태그 유사도 계산 (포트폴리오별 FAISS 사용)**  
         - 전처리 과정에서 DB 내 각 포트폴리오의 태그 리스트를 개별적으로 임베딩하여 FAISS 인덱스를 생성한 후,  
           사용자 요청의 `tags`와 포트폴리오 태그 간 최고 유사도(최대 내적)를 계산합니다.  
         - 사전에 설정한 임계값(현재 0.5) 이하의 `tag` 유사도 값에는 벌점(penalty_factor, 현재 3.0)을 적용하여 조정하고,  
           사용자 요청의 모든 태그에 대해 조정된 유사도의 평균을 산출하여 각 포트폴리오의 태그 유사도 점수를 결정합니다.
           
       - **최종 점수 산출**  
         텍스트 유사도와 태그 유사도에 각각 가중치(alpha, beta)를 부여하여 최종 점수를 계산합니다.
         ```
         최종 점수 = (alpha * 텍스트 유사도) + (beta * 태그 유사도)
         ```
     - **결과 생성 및 정렬**  
       각 포트폴리오에 대해 텍스트 유사도, 태그 유사도, 최종 점수 및 추가 정보를 포함하는 결과 객체를 생성하고,  
       최종 점수를 기준으로 내림차순 정렬한 후, 결과를 LLM이 생성한 요약 및 태그 정보와 함께 리스트로 반환합니다.

- **Request 예시**
  ```json
  {
      "user_prompt": "나는 최신 트렌드를 반영한 혁신적인 광고 영상을 촬영하고 싶어. 특히, 디지털 마케팅과 관련된 포트폴리오를 보고 싶어."
  }
  ```
  #### Request Body
    | 필드명      | 타입   | 필수 여부 | 설명                                          |
    |-------------|--------|-----------|-----------------------------------------------|
    | user_prompt | string | ✅         | 사용자의 광고 촬영 요청 혹은 관련 아이디어를 담은 텍스트 |

- **Response 예시**
    ```json
    {
        "generated": {
            "tags": ["디지털 마케팅", "혁신", "트렌드"],
            "summary": "최신 트렌드를 반영한 혁신적인 광고 영상 촬영 요청"
        },
        "search_results": [
            {
                "ptfo_seqno": 1001,
                "ptfo_nm": "포트폴리오 A",
                "ptfo_desc": "혁신적인 디지털 광고 영상",
                "text_score": 0.92,
                "tag_score": 0.85,
                "final_score": 0.88,
                "tag_names": ["디지털 마케팅", "혁신"]
            },
            {
                "ptfo_seqno": 1002,
                "ptfo_nm": "포트폴리오 B",
                "ptfo_desc": "최신 트렌드 기반 광고 영상",
                "text_score": 0.90,
                "tag_score": 0.80,
                "final_score": 0.85,
                "tag_names": ["트렌드", "광고"]
            }
        ]
    }
  ```
  #### Response Body
    
    | 필드명         | 타입   | 설명                                                       |
    |----------------|--------|------------------------------------------------------------|
    | generated      | object | LLM이 생성한 결과로, 광고 요청 요약 및 관련 태그 정보 포함        |
    | &nbsp;&nbsp; tags      | array  | LLM이 추출한 광고 관련 태그 리스트                              |
    | &nbsp;&nbsp; summary   | string | LLM이 요약한 광고 요청 내용                                   |
    | search_results | array  | 포트폴리오 검색 결과 리스트, 각 항목은 포트폴리오 정보와 유사도 점수 포함 |
    | &nbsp;&nbsp; ptfo_seqno  | number | 포트폴리오의 고유 식별 번호                                   |
    | &nbsp;&nbsp; ptfo_nm     | string | 포트폴리오 이름                                             |
    | &nbsp;&nbsp; ptfo_desc   | string | 포트폴리오 설명                                             |
    | &nbsp;&nbsp; text_score  | number | 포트폴리오 텍스트 기반 유사도 점수                             |
    | &nbsp;&nbsp; tag_score   | number | 포트폴리오 태그 기반 유사도 점수                              |
    | &nbsp;&nbsp; final_score | number | 텍스트 점수와 태그 점수를 가중 평균하여 산출한 최종 점수             |
    | &nbsp;&nbsp; tag_names   | array  | 해당 포트폴리오에 연결된 태그 리스트                           |


