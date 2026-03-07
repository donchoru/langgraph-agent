"""FastAPI 래퍼 — LangGraph 물류 에이전트를 OpenAI 호환 API로 노출."""
import time
import uuid
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import LLM_MODEL, DB_PATH
from graph.workflow import build_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 세션별 대화 이력 (메모리)
_sessions: dict[str, list[dict]] = {}
_app_graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _app_graph
    # DB 초기화 (없으면 seed)
    if not DB_PATH.exists():
        logger.info("DB 없음 — seed 실행")
        from db.seed import seed
        seed()
    _app_graph = build_graph()
    logger.info("LangGraph 워크플로우 빌드 완료")
    yield


app = FastAPI(
    title="LangGraph Logistics Agent API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 요청/응답 모델 (OpenAI 호환) ──

class ChatMessage(BaseModel):
    role: str = "user"
    content: str = ""


class ChatRequest(BaseModel):
    model: str = "langgraph-logistics"
    messages: list[ChatMessage] = Field(default_factory=list)
    temperature: float | None = None
    session_id: str | None = None  # 멀티턴용 세션 ID


class Choice(BaseModel):
    index: int = 0
    message: ChatMessage
    finish_reason: str = "stop"


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[Choice]
    usage: Usage = Usage()


# ── 엔드포인트 ──

@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completions(req: ChatRequest):
    """OpenAI 호환 Chat Completions 엔드포인트."""
    if not req.messages:
        raise HTTPException(400, "messages가 비어 있습니다.")

    # 마지막 user 메시지 추출
    user_input = ""
    for msg in reversed(req.messages):
        if msg.role == "user":
            user_input = msg.content
            break

    if not user_input:
        raise HTTPException(400, "user 메시지가 없습니다.")

    # 세션 이력
    session_id = req.session_id or "default"
    history = _sessions.get(session_id, [])

    try:
        result = _app_graph.invoke({
            "messages": [],
            "intent": "",
            "intent_detail": "",
            "trace_log": [],
            "user_input": user_input,
            "final_answer": "",
            "conversation_history": list(history),
        })

        answer = result.get("final_answer", "응답을 생성하지 못했습니다.")
        intent = result.get("intent", "unknown")

        # 이력 저장 (최근 10턴)
        history.append({
            "user": user_input,
            "answer": answer[:300],
            "intent": intent,
        })
        _sessions[session_id] = history[-10:]

    except Exception as e:
        logger.error(f"Agent 실행 오류: {e}", exc_info=True)
        raise HTTPException(500, f"Agent 실행 오류: {e}")

    return ChatResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
        created=int(time.time()),
        model=req.model,
        choices=[Choice(
            message=ChatMessage(role="assistant", content=answer),
        )],
    )


@app.get("/v1/models")
async def list_models():
    """모델 목록 — Open WebUI가 모델 발견에 사용."""
    return {
        "object": "list",
        "data": [
            {
                "id": "langgraph-logistics",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "langgraph-agent",
            }
        ],
    }


@app.get("/health")
async def health():
    return {"status": "ok", "model": LLM_MODEL, "db": str(DB_PATH)}


@app.post("/sessions/{session_id}/clear")
async def clear_session(session_id: str):
    """세션 대화 이력 초기화."""
    _sessions.pop(session_id, None)
    return {"status": "cleared", "session_id": session_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8500)
