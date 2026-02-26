"""의도분석 Agent — 사용자 질문을 의도로 분류."""
import json
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.state import AgentState, dump_state
from agents.prompts import INTENT_SYSTEM_PROMPT
from config import GEMINI_API_KEY, GEMINI_MODEL


llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0,
)


def _build_context(user_input: str, history: list[dict]) -> str:
    """대화 이력이 있으면 문맥을 포함한 프롬프트 생성."""
    if not history:
        return user_input
    ctx_lines = ["[이전 대화 이력]"]
    for h in history[-5:]:  # 최근 5턴
        ctx_lines.append(f"사용자: {h['user']}")
        ctx_lines.append(f"의도: {h.get('intent', '')}")
        ctx_lines.append(f"응답 요약: {h.get('answer', '')[:150]}")
        ctx_lines.append("")
    ctx_lines.append(f"[현재 질문]\n{user_input}")
    ctx_lines.append("")
    ctx_lines.append("위 대화 이력을 참고하여 현재 질문의 의도를 분석하세요.")
    ctx_lines.append("'그럼', '거기', '그 설비' 등 대명사는 이전 대화에서 언급된 대상을 참조합니다.")
    return "\n".join(ctx_lines)


def intent_node(state: AgentState) -> dict:
    """의도분석 노드 — 사용자 입력을 분류하고 trace_log에 기록."""
    user_input = state["user_input"]
    history = state.get("conversation_history", [])

    prompt_text = _build_context(user_input, history)
    response = llm.invoke([
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=prompt_text),
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

    # 트레이스 로그 — State 전후 스냅샷 포함
    trace = [
        f"## Step 1: IntentAgent (의도분석)",
        f"### State BEFORE",
    ]
    trace += dump_state(state)

    trace += [
        f"### LLM 호출",
        f"- input: `{user_input}`",
        f"### LLM 출력",
        f"- intent: `{intent}`",
        f"- detail: `{detail}`",
        f"- reasoning: {reasoning}",
    ]

    # 업데이트될 state를 미리 구성하여 AFTER 스냅샷 생성
    updated = dict(state)
    updated["intent"] = intent
    updated["intent_detail"] = detail

    trace += [f"### State AFTER"]
    trace += dump_state(updated)

    return {
        "intent": intent,
        "intent_detail": detail,
        "trace_log": state.get("trace_log", []) + trace,
    }
