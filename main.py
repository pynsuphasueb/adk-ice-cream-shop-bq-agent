from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from icecream_shop_agent.agent import root_agent
from pydantic import BaseModel

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "icecream_shop_app")
USER_ID = os.getenv("USER_ID", "sky_user")
SESSION_ID = os.getenv("SESSION_ID", "web-session-1")
DB_URL = os.getenv("DB_URL", "sqlite:///./adk_sessions.db")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")


async def ensure_session(
    session_service: DatabaseSessionService,
    app_name: str,
    user_id: str,
    session_id: str,
    initial_state: dict[str, Any] | None = None,
) -> None:
    existing = await session_service.list_sessions(app_name=app_name, user_id=user_id)
    if not any(s.id == session_id for s in existing.sessions):
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=initial_state or {},
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    session_service = DatabaseSessionService(db_url=DB_URL)
    await ensure_session(
        session_service,
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        initial_state={"user_name": "Sky"},
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    app.state.session_service = session_service
    app.state.runner = runner

    yield


app = FastAPI(title="ADK BigQuery Agent API", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS] if CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")


class AskBody(BaseModel):
    query: str


@app.get("/healthz")
async def healthz():
    return {"ok": True, "app": APP_NAME}


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.post("/api/ask", response_class=JSONResponse)
async def api_ask(body: AskBody):
    try:
        runner: Runner = app.state.runner
        content = types.Content(role="user", parts=[types.Part(text=body.query)])

        events = runner.run(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content,
        )

        final_text = ""
        for e in events:
            if e.is_final_response():
                final_text = (
                    e.content.parts[0].text if e.content and e.content.parts else ""
                )

        return {"ok": True, "message": final_text}

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc
