"""의도분석 Agent — 사용자 질문을 의도로 분류."""
import json
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.state import AgentState
from agents.prompts import INTENT_SYSTEM_PROMPT
from config import GEMINI_API_KEY, GEMINI_MODEL


llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0,
)


def intent_node(state: AgentState) -> dict:
    """의도분석 노드 — 사용자 입력을 분류하고 trace_log에 기록."""
    user_input = state["user_input"]

    response = llm.invoke([
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=user_input),
    ])

    raw = response.content.strip()
    # JSON 블록 추출 (```json ... ``` 감싸기 대응)
    if "```" in raw:
        raw = raw.split("```json")[-1].split("```")[0].strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"intent": "general_chat", "detail": {}, "reasoning": "JSON 파싱 실패"}

    intent = parsed.get("intent", "general_chat")
    detail = json.dumps(parsed.get("detail", {}), ensure_ascii=False)
    reasoning = parsed.get("reasoning", "")

    # 트레이스 로그
    trace = [
        f"## Step 1: IntentAgent (의도분석)",
        f"### INPUT",
        f"```\n{user_input}\n```",
        f"### OUTPUT",
        f"- intent: `{intent}`",
        f"- detail: `{detail}`",
        f"- reasoning: {reasoning}",
    ]

    return {
        "intent": intent,
        "intent_detail": detail,
        "trace_log": state.get("trace_log", []) + trace,
    }
