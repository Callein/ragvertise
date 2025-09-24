# RAGvertise
![KTL Certified](https://img.shields.io/badge/KTL-Certified-success) ![Latency-2.66s](https://img.shields.io/badge/Latency-2.66s-informational) ![ROUGE1F1-0.91](https://img.shields.io/badge/ROUGE--1%20F1-0.91-blue)  

## 📑 목차

- [RAGvertise](#ragvertise)
  - [📑 목차](#-목차)
  - [1️⃣ 프로젝트 개요](#1️⃣-프로젝트-개요)
  - [2️⃣ 설치 및 초기 설정](#2️⃣-설치-및-초기-설정)
    - [📌 2.1 필수 요구사항](#-21-필수-요구사항)
    - [📌 2.2 프로젝트 클론 및 가상 환경 설정](#-22-프로젝트-클론-및-가상-환경-설정)
    - [📌 2.3 .env 설정 (환경 변수)](#-23-env-설정-환경-변수)
    - [📌 2.4 Ollama 설치 및 모델 다운로드](#-24-ollama-설치-및-모델-다운로드)
    - [📌 2.5 fastText 모델 설정](#-25-fasttext-모델-설정)
      - [1) 모델 다운로드](#1-모델-다운로드)
      - [2) 프로젝트 내 경로 배치](#2-프로젝트-내-경로-배치)
      - [3) 주의사항](#3-주의사항)
  - [3️⃣ FastAPI 서버 실행](#3️⃣-fastapi-서버-실행)
  - [4️⃣ 주요 API](#4️⃣-주요-api)
    - [🔹 4.1 모델 테스트 API V1 (POST /api/test/generate)](#-41-모델-테스트-api-v1-post-apitestgenerate)
    - [🔹 4.2 포트폴리오 랭크 리스트 생성 API V1 (POST /api/rank/ptfo)](#-42-포트폴리오-랭크-리스트-생성-api-v1-post-apirankptfo)
      - [Request Body](#request-body)
    - [📌 5.3 환경 변수 설정](#-53-환경-변수-설정)
    - [📌 5.4 개발 서버 실행](#-54-개발-서버-실행)
    - [📌 5.5 빌드 및 배포](#-55-빌드-및-배포)
  - [6️⃣ KTL 시험 성적 요약](#6️⃣-ktl-시험-성적-요약)
    - [📊 시험 결과 요약](#-시험-결과-요약)
    - [🛠️ 시험 환경](#️-시험-환경)

<a id="1-프로젝트-개요"></a>
## 1️⃣ 프로젝트 개요
> 이 프로젝트는 FastAPI 기반의 광고 제작사 추천 서비스로,
광고 요청 문장을 LLM(Gemini, Mistral 등)으로 분석해 핵심 요소를 추출하고,
FAISS 벡터 검색을 통해 유사 포트폴리오와 광고 업체를 랭킹합니다.
데이터베이스는 MySQL을 사용하며, 백엔드와 프론트엔드(React + Vite)가 함께 구성되어 있습니다.
추가로, 생성형 AI를 활용해 광고 작업지시서 예시를 자동 생성하는 기능을 제공합니다.

> 이 프로젝트는 **한국산업기술시험원(KTL) 공식 성능 평가(19p 성적서)**를 획득했으며, 주요 결과와 환경은 [**6. KTL 시험 성적 요약**](#6-ktl-시험-성적-요약)에서 확인할 수 있습니다.
> 
<a id="2-설치-및-초기-설정"></a>
## 2️⃣ 설치 및 초기 설정
<a id="21-필수-요구사항"></a>
### 📌 2.1 필수 요구사항
- **Python 3.10 이상** (`python --version`으로 확인)  
- **pip** 및 가상환경 도구(`venv` 또는 `conda`)  
- **MariaDB 10.6 이상** 또는 **MySQL 8.0 이상**  
- **Node.js 18 이상** (프론트엔드 개발 및 빌드용)  
- **FastAPI & Uvicorn** (백엔드 실행)  
- **FAISS** (벡터 검색 인덱스)  
- **SentenceTransformers**, **fastText** (임베딩 생성)  
  - fastText 모델(`.bin` 파일) 사전 다운로드 필요 (예: `cc.ko.300.bin` for Korean)
- **Google Gemini API** 또는 **Ollama** (LLM 호출)

<a id="22-프로젝트-클론-및-가상-환경-설정"></a>
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


<a id="23-env-설정-환경-변수"></a>
### 📌 2.3 .env 설정 (환경 변수)
- 환경 변수 예시는 **[.env.example](./.env.example)** 파일을 참고하세요.
- `.env.example`를 복사하여 `.env`로 이름 변경 후, 각 항목을 환경에 맞게 수정합니다.

<a id="24-ollama-설치-및-모델-다운로드"></a>
### 📌 2.4 Ollama 설치 및 모델 다운로드
> Gemini 만 사용시에는 ollama까지 설치하실 필요는 없습니다.
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

<a id="25-fasttext-모델-설정"></a>
### 📌 2.5 fastText 모델 설정
이 프로젝트에서는 `what` 요소 임베딩 계산에 **fastText**를 사용합니다.  
이를 위해 사전에 fastText 모델(`.bin` 파일)을 다운로드하여 지정된 경로에 배치해야 합니다.

#### 1) 모델 다운로드
- [fastText 공식 제공 모델](https://fasttext.cc/docs/en/crawl-vectors.html) 또는 [한국어 모델](https://fasttext.cc/docs/en/crawl-vectors.html#models) 다운로드  
  예시 (한국어 300차원 모델):
  ```bash
  wget https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.ko.300.bin.gz
  gunzip cc.ko.300.bin.gz
  ```
#### 2) 프로젝트 내 경로 배치
- .env 파일 또는 설정에서 WORD_EMBEDDING_MODEL_PATH 항목에 해당 모델 경로를 지정
```env
WORD_EMBEDDING_MODEL_PATH=./models/cc.ko.300.bin
```
#### 3) 주의사항
- fastText .bin 파일은 용량이 크므로 Git에 포함하지 말고 .gitignore에 등록하세요.
- 모델 경로가 잘못되면 임베딩 생성 시 FileNotFoundError가 발생합니다.

<a id="3-fastapi-서버-실행"></a>
## 3️⃣ FastAPI 서버 실행
```shell
# 단순 실행
python main.py
# reload 필요시
uvicorn main:app --reload --port 9000
```
Port는 `9000` 입니다.

<a id="4-주요-api"></a>
## 4️⃣ 주요 API
[📜 Swagger UI (Docs)](http://localhost:9000/docs)  
[📃 Redoc (Alternative Docs)](http://localhost:9000/redoc)

<a id="41-모델-테스트-api-v1-post-apitestgenerate"></a>
### 🔹 4.1 모델 테스트 API V1 (POST /api/test/generate)
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

<a id="42-포트폴리오-랭크-리스트-생성-api-v1-post-apirankptfo"></a>
### 🔹 4.2 포트폴리오 랭크 리스트 생성 API V1 (POST /api/rank/ptfo)
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



<a id="43-포트폴리오-랭크-리스트-생성-api-v3-post-apiv3rankportfoliosby-ad-elements"></a>
### 🔹 4.3 포트폴리오 랭크 리스트 생성 API V3 (POST /api/v3/rank/portfolios/by-ad-elements)
> 이 API는 사용자가 직접 입력한 광고 요청(혹은 추출된 광고 요소 데이터)을 기반으로, 포트폴리오(광고 제작 사례) 리스트의 순위를 산출합니다.  
> V2와 달리 V3는 `desc`, `what`, `how`, `style` 네 가지 광고 요소를 기반으로 세분화된 유사도 점수를 계산하며, fastText와 SBERT를 혼합 사용합니다.

1. **광고 요소 입력**
   - 사용자가 직접 `desc`, `what`, `how`, `style`를 입력하거나, 별도의 추출 API(`/api/v3/ad-element/extract`)로부터 생성된 값을 전달합니다.
   - 각 요소의 의미:
     - **desc**: 광고의 한 문장 요약
     - **what**: 무엇을 광고하는지 (중분류, 단어 단위)
     - **how**: 어떤 방식/매체/도구로 광고하는지
     - **style**: 광고의 톤/연출 스타일 (단어 단위)

2. **포트폴리오 검색 및 순위 산출**
   - **요소별 임베딩 생성**
     - **SBERT** (`SentenceTransformer`) → `full`, `desc`, `how`, `style` 요소에 사용  
     - **fastText** (`cc.ko.300.bin`) → `what` 요소에 사용
   - **요소별 유사도 계산**
     - L2 정규화된 벡터 간 내적을 통해 코사인 유사도를 계산
   - **가중치 적용 후 최종 점수 산출**
     ```text
     final_score =
       full_score × 1.0 +
       desc_score × 0.6 +
       what_score × 1.5 +
       how_score × 0.2 +
       style_score × 0.5
     ```
   - **결과 생성 및 정렬**
     - 각 포트폴리오에 대해 요소별 점수, 최종 점수, 메타데이터(제작사, 제작비, 제작기간 등)를 포함한 객체 생성
     - 최종 점수 기준 내림차순 정렬 후 반환

- **Request 예시**
    ```json
    {
      "desc": "여성 건강을 위한 Y존 케어를 돕는 유산균 제품의 따뜻하고 편안한 이미지를 담은 광고.",
      "what": "건강",
      "how": "영상",
      "style": "친근함",
      "diversity": false,
      "limit": 5
    }
    ```

#### Request Body
| 필드명       | 타입    | 필수 여부 | 설명                                         |
|--------------|--------|-----------|----------------------------------------------|
| desc         | string | ✅         | 광고를 한 문장으로 요약한 설명               |
| what         | string | ✅         | 무엇을 광고하는지(중분류, 한 단어)           |
| how          | string | ✅         | 어떤 방식/매체/도구로 광고하는지             |
| style        | string | ✅         | 광고의 톤/연출 스타일(한 단어)               |
| diversity    | bool   | ❌         | 결과 다양성 반영 여부 (기본값: false)        |
| limit        | number | ❌         | 반환할 포트폴리오 개수 제한 (기본값 없음)    |

- **Response 예시**
    ```json
    {
      "generated": {
        "desc": "여성 건강을 위한 Y존 케어를 돕는 유산균 제품의 따뜻하고 편안한 이미지를 담은 광고.",
        "what": "건강",
        "how": "영상",
        "style": "친근함"
      },
      "search_results": [
        {
          "ptfo_seqno": 1012,
          "ptfo_nm": "닿기를 젤 타입 쇼츠",
          "ptfo_desc": "유산균 Y존 케어 제품 닿기를 젤 타입 쇼츠 영상입니다.",
          "final_score": 3.49,
          "desc": "y존 케어 제품의 특징을 보여주는 젤 타입 쇼츠 영상",
          "desc_score": 0.86,
          "what": "건강",
          "what_score": 1.0,
          "how": "숏폼",
          "how_score": 0.80,
          "style": "정보전달",
          "style_score": 0.77,
          "tags": ["홍보영상", "기록/정보전달", "브랜딩", "숏폼", "제품/기술"],
          "view_lnk_url": "https://player.vimeo.com/video/878209021",
          "prdn_stdo_nm": "Calmpictures",
          "prdn_cost": null,
          "prdn_perd": "2주"
        }
      ],
      "top_studios": [
        {
          "name": "Calmpictures",
          "count": 3,
          "ratio": 0.3
        },
        {
          "name": "D.NABI",
          "count": 1,
          "ratio": 0.1
        }
      ],
      "candidate_size": 10
    }
    ```
#### Response Body

| 필드명          | 타입    | 설명                                                                 |
|-----------------|--------|----------------------------------------------------------------------|
| generated       | object | 입력값 기반으로 LLM이 생성한 광고 요소(desc, what, how, style)         |
| ├─ desc         | string | 광고의 한 문장 설명                                                   |
| ├─ what         | string | 광고 대상 (예: 건강, 교육, 뷰티 등)                                   |
| ├─ how          | string | 광고 방식/매체 (예: 영상, 숏폼 등)                                    |
| ├─ style        | string | 광고 스타일 (예: 친근함, 세련된 등)                                   |
| search_results  | array  | 포트폴리오 검색 결과 리스트                                           |
| ├─ ptfo_seqno   | number | 포트폴리오 고유 식별 번호                                             |
| ├─ ptfo_nm      | string | 포트폴리오 이름                                                      |
| ├─ ptfo_desc    | string | 포트폴리오 설명                                                      |
| ├─ final_score  | number | 전체 요소 유사도 가중합으로 계산된 최종 점수                          |
| ├─ desc         | string | 매칭된 포트폴리오의 광고 설명                                         |
| ├─ desc_score   | number | desc 요소 유사도 점수                                                 |
| ├─ what         | string | 매칭된 광고 대상                                                      |
| ├─ what_score   | number | what 요소 유사도 점수                                                 |
| ├─ how          | string | 매칭된 광고 방식                                                      |
| ├─ how_score    | number | how 요소 유사도 점수                                                  |
| ├─ style        | string | 매칭된 광고 스타일                                                    |
| ├─ style_score  | number | style 요소 유사도 점수                                                |
| ├─ tags         | array  | 포트폴리오 관련 태그 리스트                                            |
| ├─ view_lnk_url | string | 영상 URL (없을 수 있음)                                               |
| ├─ prdn_stdo_nm | string | 제작 스튜디오명 (없을 수 있음)                                        |
| ├─ prdn_cost    | number | 제작비 (없을 수 있음)                                                 |
| ├─ prdn_perd    | string | 제작기간 (없을 수 있음)                                               |
| top_studios     | array  | 후보 중 상위 스튜디오 리스트                                          |
| ├─ name         | string | 스튜디오명                                                            |
| ├─ count        | number | 해당 스튜디오 포트폴리오 수                                           |
| ├─ ratio        | number | 후보 대비 비율                                                        |
| candidate_size  | number | 전체 후보 개수                                                        |


<a id="44-광고-작업지시서-예시-생성-api-v3-post-apiv3production_examplegenerate"></a>
### 🔹 4.4 광고 작업지시서 예시 생성 API V3 (POST `/api/v3/production_example/generate`)

> 이 API는 **랭크 검색 결과**를 기반으로 광고 제작에 필요한 **작업지시서 예시 텍스트**를 자동으로 생성합니다.  
> 프론트엔드에서 `/api/v3/rank/portfolios/by-ad-elements` 호출 결과를 그대로 전달하는 것을 권장합니다.

---

#### 1. 처리 방식
1. **요청 데이터 수집**  
   - `generated`: 사용자의 광고 요청을 LLM이 분석한 핵심 광고 요소(desc, what, how, style)
   - `search_results`: 추천 포트폴리오 목록 (점수 및 메타 정보 포함)
   - `top_studios`: 상위 스튜디오 통계
   - `candidate_size`: 후보 개수

2. **LLM 기반 예시 생성**  
   - 광고 요소와 포트폴리오 정보를 기반으로, 실무에 바로 참고할 수 있는 광고 작업지시서 예시를 작성.
   - 결과는 **자연어 텍스트** 형태로 반환.

---

#### 2. Request 예시
    ```json
    {
      "generated": {
        "desc": "여성 건강을 위한 Y존 케어를 돕는 유산균 제품의 따뜻하고 편안한 이미지를 담은 광고.",
        "what": "건강",
        "how": "영상",
        "style": "친근함"
      },
      "search_results": [
        {
          "final_score": 3.48,
          "full_score": 0.93,
          "desc_score": 0.86,
          "what_score": 1.0,
          "how_score": 0.79,
          "style_score": 0.76,
          "desc": "y존 케어 제품의 특징을 보여주는 젤 타입 쇼츠 영상",
          "what": "건강",
          "how": "숏폼",
          "style": "정보전달",
          "ptfo_seqno": 1012,
          "ptfo_nm": "닿기를 젤 타입 쇼츠",
          "ptfo_desc": "유산균 Y존 케어 제품 닿기를 젤 타입 쇼츠 영상입니다.",
          "tags": ["홍보영상", "기록/정보전달", "브랜딩", "숏폼", "제품/기술"],
          "view_lnk_url": "https://...",
          "prdn_stdo_nm": "Calmpictures",
          "prdn_cost": null,
          "prdn_perd": "2주"
        }
      ],
      "top_studios": [
        { "name": "Calmpictures", "count": 3, "ratio": 0.3 }
      ],
      "candidate_size": 10
    }
    ```
#### 3. Request Body

| 필드명           | 타입     | 필수 | 설명 |
|------------------|----------|------|------|
| `generated`      | object   | ✅ | LLM이 생성한 광고 핵심 요소 |
| ├─ `desc`        | string   | ✅ | 광고 한 문장 설명 |
| ├─ `what`        | string   | ✅ | 광고 대상(카테고리, 한 단어) |
| ├─ `how`         | string   | ✅ | 광고 매체/방식 |
| ├─ `style`       | string   | ✅ | 광고 스타일/톤 |
| `search_results` | array    | ✅ | 추천 포트폴리오 목록 |
| ├─ `final_score` | number   | ✅ | 최종 점수 |
| ├─ `full_score`  | number   | ✅ | 전체 요소 결합 유사도 점수 |
| ├─ `desc_score`  | number   | ✅ | desc 유사도 점수 |
| ├─ `what_score`  | number   | ✅ | what 유사도 점수 |
| ├─ `how_score`   | number   | ✅ | how 유사도 점수 |
| ├─ `style_score` | number   | ✅ | style 유사도 점수 |
| ├─ `desc`        | string   | ✅ | 포트폴리오 desc 값 |
| ├─ `what`        | string   | ✅ | 포트폴리오 what 값 |
| ├─ `how`         | string   | ✅ | 포트폴리오 how 값 |
| ├─ `style`       | string   | ✅ | 포트폴리오 style 값 |
| ├─ `ptfo_seqno`  | number   | ✅ | 포트폴리오 고유 ID |
| ├─ `ptfo_nm`     | string   | ✅ | 포트폴리오 이름 |
| ├─ `ptfo_desc`   | string   | ✅ | 포트폴리오 설명 |
| ├─ `tags`        | array    | ✅ | 태그 목록 |
| ├─ `view_lnk_url`| string   | ❌ | 영상 링크 URL |
| ├─ `prdn_stdo_nm`| string   | ❌ | 제작 스튜디오 이름 |
| ├─ `prdn_cost`   | number   | ❌ | 제작 비용 |
| ├─ `prdn_perd`   | string   | ❌ | 제작 기간 |
| `top_studios`    | array    | ✅ | 상위 스튜디오 통계 (`name`, `count`, `ratio`) |
| `candidate_size` | number   | ✅ | 후보 개수 |

#### 4. Response 예시
    ```json
    {
      "example": "제작 목적: 여성 건강을 위한 Y존 케어 유산균 제품의 브랜드 인지도 향상 및 구매 유도.\n\n광고 콘셉트: 따뜻하고 편안한 분위기 속에서 제품의 효능과 사용법을 자연스럽게 전달.\n\n제작 형식: 영상 (숏폼 및 중·장편 혼합)\n\n스타일: 친근하고 편안한 연출, 일상 속에서 자연스럽게 스며드는 장면 구성.\n\n참고 포트폴리오:\n1. 메큐릭 닿기를 젤 타입 쇼츠 - Calmpictures (https://player.vimeo.com/video/878209021)\n2. 메큐릭 닿기를 스프레이형 쇼츠 - Calmpictures (https://player.vimeo.com/video/878208992)\n3. 무앤유 - 봉랩 (https://player.vimeo.com/video/859290615)\n\n제작 조건:\n- 주요 타겟: 20~40대 여성\n- 촬영 장소: 따뜻하고 아늑한 실내 공간\n- 제작 기간: 2주~1개월\n- 필요 인력: 모델(여성), 촬영감독, 조명감독, 편집자\n\n예상 제작비: 스튜디오별 제안서 참고"
    }
    ```

#### 5. Response Body

| 필드명  | 타입     | 설명                                                                 |
|---------|----------|----------------------------------------------------------------------|
| example | string   | 생성된 광고 작업지시서 예시 텍스트. 제작 목적, 콘셉트, 형식, 스타일, 참고 포트폴리오, 제작 조건, 예상 제작비 등의 내용을 포함 |
> 프런트엔드에서 바로 복사가능

<a id="5-프런트엔드-실행-가이드"></a>
## 5️⃣ 프런트엔드 실행 가이드

<a id="51-필수-요구사항"></a>
### 📌 5.1 필수 요구사항
- Node.js 18 이상
- npm 9 이상 또는 pnpm, yarn (패키지 매니저는 자유 선택)


<a id="52-프로젝트-클론-및-의존성-설치"></a>
### 📌 5.2 프로젝트 클론 및 의존성 설치
```bash
# frontend 디렉토리로 이동
cd frontend

# 패키지 설치
npm install
# 또는
yarn install
# 또는
pnpm install
```

<a id="53-환경-변수-설정"></a>
### 📌 5.3 환경 변수 설정

- frontend/.env 파일을 생성하고 백엔드 URL을 기입합니다.
```env
VITE_API_BASE_URL=http://localhost:9000
```

<a id="54-개발-서버-실행"></a>
### 📌 5.4 개발 서버 실행

```bash
npm run dev
# 또는
yarn dev
# 또는
pnpm dev
```

<a id="55-빌드-및-배포"></a>
### 📌 5.5 빌드 및 배포
```bash
npm run build
# 또는
yarn build
# 또는
pnpm build
```

<a id="6-ktl-시험-성적-요약"></a>
## 6️⃣ KTL 시험 성적 요약

이 프로젝트는 한국산업기술시험원(KTL)에서 **공식 성능 평가**를 받았으며, 총 **19페이지** 분량의 시험 성적서가 발급되었습니다.  
- **Report No.** 25-054618-01-1  
- **발급일자** 2025-08-29  
- 본 README에는 요약 정보만 게시합니다.

### 📊 시험 결과 요약
> ✅ 본 섹션은 KTL 공식 시험 성적서의 요약본입니다.  

| 항목                               | 기준                 | 측정 결과 |
|-----------------------------------|----------------------|-----------|
| 고객 대화 응답 시간                | ≤ 5.00 s             | **2.66 s** |
| 대화모델 품질(키워드 추출)         | ROUGE-1 F1 ≥ 0.90    | **0.91** |
| 지식 생성 품질                     | ROUGE-1 F1 ≥ 0.40    | **0.63** |
| 촬영 레퍼런스 분류 정확도         | ROUGE-1 F1 ≥ 0.95    | **0.98** |
| 매칭 알고리즘 정확도              | Recall@5 ≥ 0.19      | **0.87** |
| 매칭 알고리즘 처리 시간           | ≤ 0.50 s             | **0.25 s** |

### 🛠️ 시험 환경

- **Hardware:** Apple M2 (8-core CPU, 10-core GPU), RAM 16GB, macOS Sequoia 15.6  
- **Software:** Python 3.11.13, PyCharm 2025.2, fastText 0.9.3, SentenceTransformers 3.4.1, faiss-cpu 1.10.0, huggingface-hub 0.28.1, Ollama 0.4.7 (Mistral 7B v0.3)  
- **Architecture:** Client v1.0 ↔ API Server v1.0 (LLM 기반 요소 추출/추천)
