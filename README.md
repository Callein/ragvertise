# RAGvertise
English | [한국어](./README_KOR.md)
![KTL Certified](https://img.shields.io/badge/KTL-Certified-success) ![Latency-2.66s](https://img.shields.io/badge/Latency-2.66s-informational) ![ROUGE1F1-0.91](https://img.shields.io/badge/ROUGE--1%20F1-0.91-blue)  

## 📑 Table of Contents

- [RAGvertise](#ragvertise)
  - [📑 Table of Contents](#-table-of-contents)
  - [1️⃣ Project Overview](#1️⃣-project-overview)
  - [2️⃣ Setup \& Initialization](#2️⃣-setup--initialization)
    - [📌 2.1 Prerequisites](#-21-prerequisites)
    - [📌 2.2 Project Clone \& Virtual Environment Setup](#-22-project-clone--virtual-environment-setup)
    - [📌 2.3 .env Setup (Environment Variables)](#-23-env-setup-environment-variables)
    - [📌 2.4 Install Ollama \& Download Models](#-24-install-ollama--download-models)
    - [📌 2.5 fastText Model Setup](#-25-fasttext-model-setup)
      - [1) Download Model](#1-download-model)
      - [2) Place in Project Path](#2-place-in-project-path)
      - [3) Notes](#3-notes)
  - [3️⃣ Run FastAPI Server](#3️⃣-run-fastapi-server)
  - [4️⃣ Main APIs](#4️⃣-main-apis)
    - [🔹 4.1 Model Test API V1 (POST /api/test/generate)](#-41-model-test-api-v1-post-apitestgenerate)
    - [🔹 4.2 Portfolio Ranking API V1 (POST /api/rank/ptfo)](#-42-portfolio-ranking-api-v1-post-apirankptfo)
      - [Request Body](#request-body)
      - [3. Request Body](#3-request-body)
      - [4. Response Example](#4-response-example)
      - [5. Response Body](#5-response-body)
  - [5️⃣ Frontend Guide](#5️⃣-frontend-guide)
    - [📌 5.1 Prerequisites](#-51-prerequisites)
    - [📌 5.2 Clone \& Install Dependencies](#-52-clone--install-dependencies)
    - [📌 5.3 Environment Variables](#-53-environment-variables)
    - [📌 5.4 Run Dev Server](#-54-run-dev-server)
    - [📌 5.5 Build \& Deployment](#-55-build--deployment)
  - [6️⃣ KTL Test Certification](#6️⃣-ktl-test-certification)
    - [📊 Test Results Summary](#-test-results-summary)
    - [🛠️ Test Environment](#️-test-environment)

<a id="1-project-overview"></a>
## 1️⃣ Project Overview
> This project is a FastAPI-based recommendation service for ad production studios.  
It analyzes ad request text with LLMs (Gemini, Mistral, etc.) to extract key elements,  
ranks similar portfolios and studios using FAISS vector search,  
and uses MySQL as the database with a React + Vite frontend.  
It also provides automatic generation of production brief examples using generative AI.

> This project has obtained the Korea Testing Laboratory (KTL) official performance evaluation (19-page report).  
> See [6. KTL Test Certification](#6-ktl-test-certification) for the key results and environment.

<a id="2-setup-initialization"></a>
## 2️⃣ Setup & Initialization
<a id="21-prerequisites"></a>
### 📌 2.1 Prerequisites
- **Python 3.10+** (`python --version`)  
- **pip** and a virtual environment tool (`venv` or `conda`)  
- **MariaDB 10.6+** or **MySQL 8.0+**  
- **Node.js 18+** (for frontend development and build)  
- **FastAPI & Uvicorn** (backend runtime)  
- **FAISS** (vector search index)  
- **SentenceTransformers**, **fastText** (for embeddings)  
  - Pre-download fastText model (`.bin` file), e.g., `cc.ko.300.bin` for Korean
- **Google Gemini API** or **Ollama** (for LLM calls)

<a id="22-project-clone-and-virtual-environment-setup"></a>
### 📌 2.2 Project Clone & Virtual Environment Setup
```shell
# Clone the project
git clone https://github.com/Callein/ragvertise_prototype.git
cd ragvertise_prototype

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)

# Install required packages
pip install -r requirements.txt
```

<a id="23-env-setup-environment-variables"></a>
### 📌 2.3 .env Setup (Environment Variables)
- See the example in **[.env.example](./.env.example)**.
- Copy `.env.example` to `.env` and update fields for your environment.

<a id="24-install-ollama-and-download-models"></a>
### 📌 2.4 Install Ollama & Download Models
> If you are using Gemini only, you don’t need to install Ollama.
```shell
# Install Ollama (Mac)
brew install --cask ollama
# Install Ollama (Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Download OpenChat 3.5 (optional)
ollama pull openchat:3.5

# Or download Mistral 7B (lighter model)
ollama pull mistral
```

<a id="25-fasttext-model-setup"></a>
### 📌 2.5 fastText Model Setup
This project uses **fastText** for `what` element embeddings.  
Download the fastText model (`.bin`) in advance and place it at a configured path.

#### 1) Download Model
- Download from [fastText official models](https://fasttext.cc/docs/en/crawl-vectors.html) or [Korean model](https://fasttext.cc/docs/en/crawl-vectors.html#models)  
  Example (Korean 300d model):
  ```bash
  wget https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.ko.300.bin.gz
  gunzip cc.ko.300.bin.gz
  ```
#### 2) Place in Project Path
- Set the model path in `.env` for WORD_EMBEDDING_MODEL_PATH:
```env
WORD_EMBEDDING_MODEL_PATH=./models/cc.ko.300.bin
```
#### 3) Notes
- The fastText `.bin` file is large; do not commit it. Add to `.gitignore`.
- If the path is wrong, a FileNotFoundError will occur during embedding.

<a id="3-run-fastapi-server"></a>
## 3️⃣ Run FastAPI Server
```shell
# Simple run
python main.py
# With reload
uvicorn main:app --reload --port 9000
```
Port is `9000`.

<a id="4-main-apis"></a>
## 4️⃣ Main APIs
[📜 Swagger UI (Docs)](http://localhost:9000/docs)  
[📃 Redoc (Alternative Docs)](http://localhost:9000/redoc)

<a id="41-model-test-api-v1-post-apitestgenerate"></a>
### 🔹 4.1 Model Test API V1 (POST /api/test/generate)
- Request Example
    ```json
    {
        "system_prompt": "persona: 너는 최고의 광고 카피를 만드는 AI야.\n instruction: 모든 답은 한국어로 해.",
        "user_prompt": "헬스케어 제품을 위한 창의적인 광고 문구를 추천해줘."
    }
    ```
    #### Request Body
    | Field           | Type    | Required | Description                                 |
    |-----------------|---------|----------|---------------------------------------------|
    | `system_prompt` | `string`| ✅        | Model role/instructions                      |
    | `user_prompt`   | `string`| ✅        | The actual user request                      |
    

- Response Example
    ```json
    {
        "response": "1. \"체력을 강화하는 건강한 미래를 만들어라! 다양한 헬스케어 제품으로 건강하신 것처럼!\"\n\n2. \"오늘부터 건강함의 시작, 내일부터 행복한 자신과 함께하는 헬스케어 제품입니다.\"\n\n3. \"건강을 위해 가장 중요한 것은 자신의 삶! 내 삶, 내 체력, 나만의 헬스케어 제품으로 당신이 건강하시어라.\"\n\n4. \"건강함을 선택하세요. 지금부터 겸손한 시작, 건강한 미래를 만들어내세요!\"\n\n5. \"건강에서 삶의 뿌리를 발굴해보세요! 최고의 헬스케어 제품으로 건강하신 것처럼!\"\n\n6. \"행복을 위한 기원은 건강함! 건강한 체력, 건강한 마음, 건강한 삶을 위해 최고의 헬스케어 제품으로 선택해보세요.\"\n\n7. \"건강하신 것처럼 행복하시오! 혁신적인 헬스케어 제품과 함께한 당신의 건강한 삶, 건강한 미래를 만들어내세요.\"\n\n8. \"건강함을 선택하고, 행복을 누리시오! 최고의 헬스케어 제품과 함께하여 당신이 건강하시며 행복해지세요.\"\n\n9. \"건강한 체력으로 삶을 만나보세요! 최고의 헬스케어 제품과 함께, 당신의 건강한 미래를 만들어내세요.\"\n\n10. \"건강하신 것처럼 행복하시오! 최고의 헬스케어 제품과 함께, 당신의 건강한 미래를 만들어내세요.\""
    }
    ```

- You can also craft the system prompt to get a structured JSON response.
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
        "response": " {\n     \"tags\": [\"남자 아이돌\", \"춤\", \"홍보\", \"클렌징 폼\"],\n     \"summary\": \"영상에서 남자 아이돌이 춤을 추며 동시에 클랜징 폼의 거품이 나는 광고입니다. 춤과 클랜징 폼이 조합된 매력적인 모습으로 관심을 유발할 수 있을 것입니다.\"\n   }"      
      }
      ```

<a id="42-portfolio-ranking-api-v1-post-apirankptfo"></a>
### 🔹 4.2 Portfolio Ranking API V1 (POST /api/rank/ptfo)
> This API computes a ranked list of portfolios (past ad productions) based on a user’s ad request or idea.

1. **LLM summarization and tag extraction**  
   - Sends the user request and a predefined system prompt to an LLM (currently Mistral).  
   - Extracts a summary (`summary`) and ad category tags (`tags`).
   
2. **Portfolio search and ranking** 
   - **Embeddings and similarity**  
     - **Embedding model initialization**  
       Use `SentenceTransformer('all-MiniLM-L6-v2')` to embed the LLM-generated `summary` and `tags`.
     - **Text similarity (FAISS)**  
       - L2 normalize portfolio embeddings and build a FAISS `IndexFlatIP` (inner product index).  
       - Embed and normalize the user summary, then compute the inner product with portfolio embeddings (cosine-equivalent).  
       - The inner product value is the text similarity score.
     - **Tag similarity (per-portfolio FAISS)**  
       - For each portfolio, embed its tag list and build a FAISS index; compute the maximum similarity (max inner product) between each user tag and portfolio tags.  
       - Apply a penalty for low similarities (threshold 0.5; `penalty_factor` 3.0), then average adjusted similarities across all user tags to get the tag similarity score.
       
   - **Final score**  
     Assign weights (alpha, beta) to text and tag similarity to compute the final score.
     ```
     Final score = (alpha * text similarity) + (beta * tag similarity)
     ```
   - **Result building and sorting**  
     Build result objects per portfolio (text similarity, tag similarity, final score, metadata), then sort by final score (desc) and return along with the generated summary and tags.

- Request Example
  ```json
  {
      "user_prompt": "나는 최신 트렌드를 반영한 혁신적인 광고 영상을 촬영하고 싶어. 특히, 디지털 마케팅과 관련된 포트폴리오를 보고 싶어."
  }
  ```
  #### Request Body
  | Field       | Type   | Required | Description                                              |
  |-------------|--------|----------|----------------------------------------------------------|
  | user_prompt | string | ✅        | User ad request or idea text                             |

- Response Example
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
    
  | Field                | Type   | Description                                                          |
  |----------------------|--------|----------------------------------------------------------------------|
  | generated            | object | LLM-generated summary and tags                                       |
  | &nbsp;&nbsp; tags    | array  | Extracted ad-related tags                                            |
  | &nbsp;&nbsp; summary | string | LLM summary of the ad request                                        |
  | search_results       | array  | Portfolio results with similarity scores                             |
  | &nbsp;&nbsp; ptfo_seqno  | number | Portfolio ID                                                    |
  | &nbsp;&nbsp; ptfo_nm     | string | Portfolio name                                                 |
  | &nbsp;&nbsp; ptfo_desc   | string | Portfolio description                                          |
  | &nbsp;&nbsp; text_score  | number | Text-based similarity score                                    |
  | &nbsp;&nbsp; tag_score   | number | Tag-based similarity score                                     |
  | &nbsp;&nbsp; final_score | number | Weighted combination of text and tag scores                    |
  | &nbsp;&nbsp; tag_names   | array  | Tag list attached to the portfolio                             |

<a id="43-portfolio-ranking-api-v3-post-apiv3rankportfoliosby-ad-elements"></a>
### 🔹 4.3 Portfolio Ranking API V3 (POST /api/v3/rank/portfolios/by-ad-elements)
> This API ranks portfolios using user-provided ad elements (or elements extracted by a separate API).  
> Unlike V2, V3 computes granular similarity scores using four elements—`desc`, `what`, `how`, `style`—combining fastText with SBERT.

1. **Input elements**
   - Provide `desc`, `what`, `how`, `style` directly or pass values from `/api/v3/ad-element/extract`.
   - Semantics:
     - **desc**: one-sentence ad description
     - **what**: what to advertise (mid-category, single word)
     - **how**: medium/method/tool for advertising
     - **style**: tone/directing style (single word)

2. **Search and ranking**
   - **Embeddings per element**
     - **SBERT** (`SentenceTransformer`) → `full`, `desc`, `how`, `style`  
     - **fastText** (`cc.ko.300.bin`) → `what`
   - **Similarity per element**
     - Compute cosine similarity via inner product on L2-normalized vectors
   - **Weighted final score**
     ```text
     final_score =
       full_score × 1.0 +
       desc_score × 0.6 +
       what_score × 1.5 +
       how_score × 0.2 +
       style_score × 0.5
     ```
   - **Result building and sorting**
     - Include per-element scores, final score, and metadata (studio, cost, period, etc.)
     - Sort by final score (desc) and return

- Request Example
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
| Field       | Type   | Required | Description                                      |
|-------------|--------|----------|--------------------------------------------------|
| desc        | string | ✅        | One-sentence ad description                      |
| what        | string | ✅        | What to advertise (mid-category, single word)    |
| how         | string | ✅        | Medium/method/tool for advertising               |
| style       | string | ✅        | Ad tone/directing style (single word)            |
| diversity   | bool   | ❌        | Apply result diversity (default: false)          |
| limit       | number | ❌        | Max number of portfolios to return               |

- Response Example
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

| Field            | Type   | Description                                                             |
|------------------|--------|----------------------------------------------------------------------|
| generated        | object | LLM-generated ad elements (desc, what, how, style)                      |
| ├─ desc          | string | One-sentence ad description                                             |
| ├─ what          | string | Ad target (e.g., health, education, beauty)                             |
| ├─ how           | string | Ad medium/method (e.g., video, shortform)                               |
| ├─ style         | string | Ad style (e.g., friendly, refined)                                      |
| search_results   | array  | Portfolio results                                                        |
| ├─ ptfo_seqno    | number | Portfolio ID                                                             |
| ├─ ptfo_nm       | string | Portfolio name                                                           |
| ├─ ptfo_desc     | string | Portfolio description                                                    |
| ├─ final_score   | number | Weighted sum across element similarities                                 |
| ├─ desc          | string | Matched portfolio description                                            |
| ├─ desc_score    | number | Similarity score for desc                                                |
| ├─ what          | string | Matched ad target                                                        |
| ├─ what_score    | number | Similarity score for what                                                |
| ├─ how           | string | Matched ad medium                                                        |
| ├─ how_score     | number | Similarity score for how                                                 |
| ├─ style         | string | Matched ad style                                                         |
| ├─ style_score   | number | Similarity score for style                                               |
| ├─ tags          | array  | Related tag list                                                         |
| ├─ view_lnk_url  | string | Video URL (may be absent)                                                |
| ├─ prdn_stdo_nm  | string | Production studio name (may be absent)                                   |
| ├─ prdn_cost     | number | Production cost (may be absent)                                          |
| ├─ prdn_perd     | string | Production period (may be absent)                                        |
| top_studios      | array  | Top studios among candidates                                             |
| ├─ name          | string | Studio name                                                              |
| ├─ count         | number | Number of portfolios by the studio                                       |
| ├─ ratio         | number | Ratio within candidates                                                  |
| candidate_size   | number | Total number of candidates                                               |

<a id="44-production-brief-example-generation-api-v3-post-apiv3production_examplegenerate"></a>
### 🔹 4.4 Production Brief Example Generation API V3 (POST `/api/v3/production_example/generate`)

> This API generates a natural-language **production brief example** based on the **ranking results**.  
> On the frontend, pass the results from `/api/v3/rank/portfolios/by-ad-elements` as-is.

---

#### 1. Processing
1. **Collect request data**  
   - `generated`: LLM-analyzed ad elements from the user request (desc, what, how, style)
   - `search_results`: recommended portfolio list (with scores and metadata)
   - `top_studios`: top studio stats
   - `candidate_size`: number of candidates

2. **LLM-based generation**  
   - Produces a practical brief example using the elements and portfolio info.
   - Returns a **natural-language** text.

---

#### 2. Request Example
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

| Field             | Type    | Req | Description                                                   |
|------------------ |---------|-----|---------------------------------------------------------------|
| `generated`       | object  | ✅  | LLM-generated ad elements                                     |
| ├─ `desc`         | string  | ✅  | One-sentence ad description                                   |
| ├─ `what`         | string  | ✅  | Ad target (category, single word)                             |
| ├─ `how`          | string  | ✅  | Ad medium/method                                              |
| ├─ `style`        | string  | ✅  | Ad style/tone                                                 |
| `search_results`  | array   | ✅  | Recommended portfolio list                                    |
| ├─ `final_score`  | number  | ✅  | Final score                                                   |
| ├─ `full_score`   | number  | ✅  | Combined similarity score                                     |
| ├─ `desc_score`   | number  | ✅  | desc similarity score                                         |
| ├─ `what_score`   | number  | ✅  | what similarity score                                         |
| ├─ `how_score`    | number  | ✅  | how similarity score                                          |
| ├─ `style_score`  | number  | ✅  | style similarity score                                        |
| ├─ `desc`         | string  | ✅  | Portfolio desc value                                          |
| ├─ `what`         | string  | ✅  | Portfolio what value                                          |
| ├─ `how`          | string  | ✅  | Portfolio how value                                           |
| ├─ `style`        | string  | ✅  | Portfolio style value                                         |
| ├─ `ptfo_seqno`   | number  | ✅  | Portfolio ID                                                  |
| ├─ `ptfo_nm`      | string  | ✅  | Portfolio name                                                |
| ├─ `ptfo_desc`    | string  | ✅  | Portfolio description                                         |
| ├─ `tags`         | array   | ✅  | Tag list                                                      |
| ├─ `view_lnk_url` | string  | ❌  | Video URL                                                     |
| ├─ `prdn_stdo_nm` | string  | ❌  | Production studio name                                        |
| ├─ `prdn_cost`    | number  | ❌  | Production cost                                               |
| ├─ `prdn_perd`    | string  | ❌  | Production period                                             |
| `top_studios`     | array   | ✅  | Top studios (`name`, `count`, `ratio`)                        |
| `candidate_size`  | number  | ✅  | Number of candidates                                          |

#### 4. Response Example
```json
{
  "example": "제작 목적: 여성 건강을 위한 Y존 케어 유산균 제품의 브랜드 인지도 향상 및 구매 유도.\n\n광고 콘셉트: 따뜻하고 편안한 분위기 속에서 제품의 효능과 사용법을 자연스럽게 전달.\n\n제작 형식: 영상 (숏폼 및 중·장편 혼합)\n\n스타일: 친근하고 편안한 연출, 일상 속에서 자연스럽게 스며드는 장면 구성.\n\n참고 포트폴리오:\n1. 메큐릭 닿기를 젤 타입 쇼츠 - Calmpictures (https://player.vimeo.com/video/878209021)\n2. 메큐릭 닿기를 스프레이형 쇼츠 - Calmpictures (https://player.vimeo.com/video/878208992)\n3. 무앤유 - 봉랩 (https://player.vimeo.com/video/859290615)\n\n제작 조건:\n- 주요 타겟: 20~40대 여성\n- 촬영 장소: 따뜻하고 아늑한 실내 공간\n- 제작 기간: 2주~1개월\n- 필요 인력: 모델(여성), 촬영감독, 조명감독, 편집자\n\n예상 제작비: 스튜디오별 제안서 참고"
}
```

#### 5. Response Body

| Field   | Type   | Description                                                                 |
|---------|--------|-----------------------------------------------------------------------------|
| example | string | Generated production brief example text: objective, concept, format, style, references, production conditions, estimated cost |
> Can be copied directly in the frontend.

<a id="5-frontend-guide"></a>
## 5️⃣ Frontend Guide

<a id="51-prerequisites"></a>
### 📌 5.1 Prerequisites
- Node.js 18+
- npm 9+ or pnpm, yarn

<a id="52-clone-and-install-dependencies"></a>
### 📌 5.2 Clone & Install Dependencies
```bash
# Move to the frontend directory
cd frontend

# Install packages
npm install
# or
yarn install
# or
pnpm install
```

<a id="53-environment-variables"></a>
### 📌 5.3 Environment Variables

- Create `frontend/.env` and set the backend URL.
```env
VITE_API_BASE_URL=http://localhost:9000
```

<a id="54-run-dev-server"></a>
### 📌 5.4 Run Dev Server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

<a id="55-build-and-deployment"></a>
### 📌 5.5 Build & Deployment
```bash
npm run build
# or
yarn build
# or
pnpm build
```

<a id="6-ktl-test-certification"></a>
## 6️⃣ KTL Test Certification

This project has been officially tested and certified by the Korea Testing Laboratory (KTL).  
- **Report No.** 25-054618-01-1  
- **Issue Date** 2025-08-29  
- This README provides a summary only. **The full 19-page report can be provided upon request.**

### 📊 Test Results Summary
> ✅ This section contains a summarized version of the official test report.  


| Test Item                        | Requirement          | Result     |
|----------------------------------|----------------------|------------|
| Customer dialogue response time  | ≤ 5.00 s             | **2.66 s** |
| Dialogue model quality           | ROUGE-1 F1 ≥ 0.90    | **0.91**   |
| Knowledge generation quality     | ROUGE-1 F1 ≥ 0.40    | **0.63**   |
| Reference classification accuracy| ROUGE-1 F1 ≥ 0.95    | **0.98**   |
| Matching algorithm accuracy      | Recall@5 ≥ 0.19      | **0.87**   |
| Matching algorithm processing    | ≤ 0.50 s             | **0.25 s** |

### 🛠️ Test Environment

- **Hardware:** Apple M2 (8-core CPU, 10-core GPU), RAM 16GB, macOS Sequoia 15.6  
- **Software:** Python 3.11.13, PyCharm 2025.2, fastText 0.9.3, SentenceTransformers 3.4.1, faiss-cpu 1.10.0, huggingface-hub 0.28.1, Ollama 0.4.7 (Mistral 7B v0.3)  
- **Architecture:** Client v1.0 ↔ API Server v1.0 (LLM-based extraction & recommendation)