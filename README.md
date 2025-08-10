# adk-ice-cream-shop-bq-agent
**BigQuery Chat Agent — ADK + FastAPI**

Chat with BigQuery. Scoop insights.  
A sleek web chat (FastAPI + static UI) powered by **ADK**’s BigQuery toolset for read-only analytics. Markdown-ready, AI on the left / you on the right. Session state backed by SQLite.

---

## Features
- **Conversational BigQuery** (read-only via `WriteMode.BLOCKED`)
- **Clean chat UI**: AI left / You right, safe **Markdown** rendering
- **Lightweight backend**: FastAPI + ADK `Runner`
- **Session persistence**: `DatabaseSessionService` (SQLite)
- **Easy auth**: GCP ADC (`gcloud auth application-default login`) or Service Account

---

## Project Layout
```
├─ app.py                 # FastAPI API + serves static UI
├─ agent.py               # ADK agent with BigQueryToolset (read-only)
├─ static/
│  └─ index.html          # Chat UI (Tailwind + marked + DOMPurify)
├─ .env.example           # Sample env
└─ pyproject.toml         # Project + deps (uv)
```

---

## Prerequisites
- **Python** 3.11+
- **GCP project** with **BigQuery API** enabled
  ```bash
  gcloud services enable bigquery.googleapis.com
  ```
- **Auth for BigQuery** (choose one)
  - Dev machine:  
    ```bash
    gcloud auth application-default login
    gcloud config set project YOUR_PROJECT_ID
    ```
  - Or set a Service Account key:  
    `export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json`
- **Model config** (choose ONE)
  - **Google AI Studio**: `export GOOGLE_API_KEY="YOUR_AI_STUDIO_KEY"`
  - **Vertex AI**:  
    ```bash
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="us-central1"
    ```
- **Service Account (recommended, least privilege)**
  - Project role: `roles/bigquery.jobUser` *(run query jobs)*
  - Dataset role: `roles/bigquery.dataViewer` **on your target dataset only** *(read tables)*
  - **Vertex path only**: add `roles/aiplatform.user`

> Tip: In production, attach the SA to your runtime (Cloud Run/GKE/GCE) instead of using JSON keys.

---

## Setup (with **uv**)
Install [uv](https://docs.astral.sh/uv/) once, then sync deps:
```bash
# macOS/Linux installer:
curl -LsSf https://astral.sh/uv/install.sh | sh

# from repo root
uv sync
```

### Run (dev)
```bash
# model & ADC env (example: AI Studio)
export GOOGLE_API_KEY="YOUR_AI_STUDIO_KEY"
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

uv run uvicorn app:app --reload --port 8000
# open http://localhost:8000
```

---

## Setup (with **pip**)
```bash
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
# or:
# pip install fastapi "uvicorn[standard]" google-adk google-genai google-auth google-cloud-bigquery
```

### Run (pip)
```bash
export GOOGLE_API_KEY="YOUR_AI_STUDIO_KEY"
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

uvicorn app:app --reload --port 8000
```

---

## Usage
- Ask in natural language (e.g., “Top 5 branches by `total_sale` last 7 days”).
- The agent uses **BigQueryToolset** to run **read-only** queries and replies in **Markdown**.
- The UI renders lists, code blocks, and bold text safely.

---

## Run with **ADK Web** (Dev UI)
**ADK Web** is a dev UI to chat with your agent, inspect tool calls, and iterate faster.

### Requirements
- Your code exposes a module-level variable named **`root_agent`** (this repo does in `agent.py`).
- Environment set for model + BigQuery auth (same as above).

### Start the Dev UI
```bash
uv run adk web       # launch ADK Web
```
Open the printed URL (typically `http://localhost:8000`) and pick the module that exposes `root_agent`.

**If your agent doesn’t show up**
1. Ensure `root_agent` can be imported without side effects.  
2. If using a package layout, re-export it:
   ```python
   # your_package/__init__.py
   from .agent import root_agent
   ```
3. Run `uv run adk web` from the **parent folder** of the package.  

---

## Scope & Safety (recommended)
- Lock access to **one dataset** using IAM:
  - Grant `roles/bigquery.dataViewer` **only** on that dataset.
  - Grant `roles/bigquery.jobUser` at the project level.
- Keep `WriteMode.BLOCKED` in `BigQueryToolConfig` to prevent writes.
- Optionally add a simple SQL guard to reject queries outside your dataset.

---
