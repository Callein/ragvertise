# Third-Party Notices
_Last updated: 2025-09-24_

This document lists third-party software, models, datasets, tools, and frameworks used by the **RAGvertise** project.  
Please update this file as dependencies change.

---

## Libraries

> **Python (from `requirements.txt`)** — versions per repo: faiss-cpu **1.10.0**, fastapi **0.115.8**, fasttext **0.9.3**, huggingface-hub **0.28.1**, numpy **1.26.4**, ollama **0.4.7**, scikit-learn **1.6.1**, scipy **1.13.1**, sentence-transformers **3.4.1**, starlette **0.45.3**, transformers **4.48.3**, torch **2.6.0**, torchaudio **2.6.0**, torchvision **0.21.0**, uvicorn **0.34.0**, uvloop **0.21.0**, PyYAML **6.0.2**, requests **2.32.3**, SQLAlchemy **2.0.38**, etc.

- **annotated-types**
  - Version: 0.7.0
  - License: MIT (common) — verify
  - Homepage/Repo: https://pypi.org/project/annotated-types/
  - Notes: Typing helpers

- **anyio**
  - Version: 4.8.0
  - License: MIT — verify
  - Homepage/Repo: https://github.com/agronholm/anyio
  - Notes: Async networking

- **beautifulsoup4**
  - Version: 4.13.4
  - License: MIT
  - Homepage/Repo: https://www.crummy.com/software/BeautifulSoup/
  - Notes: HTML parsing

- **faiss-cpu**
  - Version: 1.10.0
  - License: MIT
  - Homepage/Repo: https://github.com/facebookresearch/faiss
  - Notes: Vector similarity

- **fastapi**
  - Version: 0.115.8
  - License: MIT
  - Homepage/Repo: https://github.com/tiangolo/fastapi
  - Notes: Backend web framework

- **fasttext**
  - Version: 0.9.3
  - License: MIT
  - Homepage/Repo: https://github.com/facebookresearch/fastText
  - Notes: Word embeddings

- **gensim**
  - Version: 4.3.3
  - License: LGPL-2.1-or-later — verify
  - Homepage/Repo: https://github.com/RaRe-Technologies/gensim
  - Notes: NLP utilities

- **google-auth / googleapis-common-protos / grpcio / grpcio-status / httplib2**
  - Version: 2.40.3 / 1.70.0 / 1.73.0 / 1.71.0 / 0.22.0
  - License: Apache-2.0 — verify
  - Homepage: various Google OSS repos
  - Notes: Google API client stack

- **google-genai**
  - Version: 1.19.0
  - License: TBD (verify on project site)
  - Homepage/Repo: https://pypi.org/project/google-genai/
  - Notes: Google Generative AI client

- **huggingface-hub**
  - Version: 0.28.1
  - License: Apache-2.0
  - Homepage/Repo: https://github.com/huggingface/huggingface_hub
  - Notes: Model hub client

- **numpy**
  - Version: 1.26.4
  - License: BSD-3-Clause
  - Homepage/Repo: https://github.com/numpy/numpy
  - Notes: Numerical computing

- **mysql-connector-python / PyMySQL / SQLAlchemy**
  - Version: 9.2.0 / 1.1.1 / 2.0.38
  - License: (Oracle) Commercial/Community / MIT / MIT — verify mysql-connector terms
  - Homepage/Repo: respective project pages
  - Notes: Database connectivity & ORM

- **ollama (Python client)**
  - Version: 0.4.7
  - License: MIT — verify
  - Homepage/Repo: https://pypi.org/project/ollama/
  - Notes: Client for local model server

- **pydantic / pydantic_core**
  - Version: 2.10.6 / 2.27.2
  - License: MIT
  - Homepage/Repo: https://github.com/pydantic/pydantic
  - Notes: Data validation

- **requests / httpx / anyio / h11 / httpcore**
  - Version: 2.32.3 / 0.28.1 / 4.8.0 / 0.14.0 / 1.0.7
  - License: Apache-2.0 (requests), BSD-3 (httpx) — verify for each
  - Homepage/Repo: respective project pages
  - Notes: HTTP clients & ASGI stack

- **scikit-learn**
  - Version: 1.6.1
  - License: BSD-3-Clause
  - Homepage/Repo: https://github.com/scikit-learn/scikit-learn
  - Notes: ML utilities

- **scipy**
  - Version: 1.13.1
  - License: BSD-3-Clause
  - Homepage/Repo: https://github.com/scipy/scipy
  - Notes: Scientific computing

- **sentence-transformers**
  - Version: 3.4.1
  - License: Apache-2.0
  - Homepage/Repo: https://github.com/UKPLab/sentence-transformers
  - Notes: SBERT embeddings

- **starlette**
  - Version: 0.45.3
  - License: BSD-3-Clause
  - Homepage/Repo: https://github.com/encode/starlette
  - Notes: ASGI toolkit (FastAPI base)

- **tokenizers**
  - Version: 0.21.0
  - License: Apache-2.0
  - Homepage/Repo: https://github.com/huggingface/tokenizers
  - Notes: HF tokenizers (Rust/Py)

- **torch / torchaudio / torchvision**
  - Version: 2.6.0 / 2.6.0 / 0.21.0
  - License: BSD-3-Clause (PyTorch) — verify
  - Homepage/Repo: https://pytorch.org/
  - Notes: Deep learning framework

- **transformers**
  - Version: 4.48.3
  - License: Apache-2.0
  - Homepage/Repo: https://github.com/huggingface/transformers
  - Notes: LLM pipelines

- **tqdm**
  - Version: 4.67.1
  - License: MIT
  - Homepage/Repo: https://github.com/tqdm/tqdm
  - Notes: Progress bars

- **uvicorn**
  - Version: 0.34.0
  - License: BSD-3-Clause
  - Homepage/Repo: https://github.com/encode/uvicorn
  - Notes: ASGI server

- **uvloop**
  - Version: 0.21.0
  - License: MIT
  - Homepage/Repo: https://github.com/MagicStack/uvloop
  - Notes: Fast event loop

> **Frontend (from `package.json`)** — dependencies: axios **^1.11.0**, react **^19.1.0**, react-dom **^19.1.0**, react-router-dom **^7.7.1**; devDependencies: @vitejs/plugin-react **^4.6.0**, vite **^7.0.4**, tailwindcss **^3.4.17**, typescript **~5.8.3**, eslint **^9.30.1** etc.

- **axios**
  - Version: ^1.11.0
  - License: MIT
  - Homepage/Repo: https://github.com/axios/axios
  - Notes: HTTP client

- **react / react-dom**
  - Version: ^19.1.0 / ^19.1.0
  - License: MIT
  - Homepage/Repo: https://react.dev/
  - Notes: UI library

- **react-router-dom**
  - Version: ^7.7.1
  - License: MIT
  - Homepage/Repo: https://github.com/remix-run/react-router
  - Notes: Routing

- **vite / @vitejs/plugin-react**
  - Version: ^7.0.4 / ^4.6.0
  - License: MIT
  - Homepage/Repo: https://vitejs.dev/
  - Notes: Build tool

- **tailwindcss / postcss / autoprefixer**
  - Version: ^3.4.17 / ^8.5.6 / ^10.4.21
  - License: MIT
  - Homepage/Repo: https://tailwindcss.com/
  - Notes: Styling toolchain

- **typescript**
  - Version: ~5.8.3
  - License: Apache-2.0
  - Homepage/Repo: https://www.typescriptlang.org/
  - Notes: TypeScript compiler

- **eslint (+ plugins)**
  - Version: ^9.30.1 (core)
  - License: MIT
  - Homepage/Repo: https://eslint.org/
  - Notes: Linting

---

## Models

- **Mistral 7B (via Ollama)**
  - Provider: Mistral AI
  - Version/Build: v0.3 (referenced)
  - License/Terms: Apache-2.0 — verify with Ollama model card
  - Source/URL: https://ollama.com/library/mistral
  - Notes: Pulled at runtime via Ollama; weights are not redistributed in this repo

- **intfloat/multilingual-e5-base**
  - Provider: intfloat (Hugging Face)
  - Version/Build: N/A
  - License/Terms: Apache-2.0 (per model card; verify)
  - Source/URL: https://huggingface.co/intfloat/multilingual-e5-base
  - Notes: Sentence embeddings; downloaded at runtime

- **fastText vectors (cc.ko.300.bin)**
  - Provider: Facebook AI / fastText
  - Version/Date: Common Crawl vectors (ko, 300d)
  - License/Terms: CC BY-SA 3.0 (per fastText site) — verify
  - Source/URL: https://fasttext.cc/docs/en/crawl-vectors.html
  - Notes: Large external file; not stored in repo

---

## Datasets

- **Internal Test Datasets (`test_data/tc*.json`)**
  - Provider: Project-internal
  - Version/Date: 2025-08 (KTL evaluation period)
  - License/Terms: Internal use only; not redistributed
  - Source/URL: Local repo paths (e.g., `test_data/tc2_dataset.json`)
  - Notes: Used for KTL certification tests

---

## Tools and Frameworks

- **Ollama**
  - Version: 0.4.7 (Python client present; server installed locally)
  - License: MIT — verify current server repo/license
  - Homepage/Repo: https://github.com/ollama/ollama
  - Notes: Local model serving runtime

- **PyCharm**
  - Version: 2025.2 (referenced)
  - License: Proprietary (JetBrains)
  - Homepage: https://www.jetbrains.com/pycharm/
  - Notes: Development IDE; not redistributed

- **macOS (Apple Silicon)**
  - Version: Sequoia 15.6 (environment)
  - License: Proprietary (Apple)
  - Homepage: https://www.apple.com/macos/
  - Notes: Host OS; not redistributed

- **MySQL / MariaDB**
  - Version: N/A
  - License: GPL-2.0 (MySQL Community), GPL-2.0 (MariaDB) — verify enterprise terms if applicable
  - Homepage: https://www.mysql.com/ / https://mariadb.org/
  - Notes: External database servers; not redistributed

---

If any license requires attribution or the inclusion of its notice text, copy the required notice(s) into this file or link to the appropriate files within the dependency.

---

### Maintenance Tips
- When you add or bump packages in `requirements.txt` or `package.json`, reflect the changes here.
- If a model or dataset’s license is unclear, mark it `TBD` and add the source URL to review before distribution.
- Keep this file in sync with your release tags.