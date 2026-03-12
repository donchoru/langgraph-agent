"""의도분석 Agent — 키워드 힌트 + LLM 판단."""
from langchain_core.messages import HumanMessage, SystemMessage
from agents.state import AgentState, dump_state
from agents.prompts import INTENT_SYSTEM_PROMPT
from config import LLM_MODEL
from llm_factory import create_llm

llm = create_llm(temperature=0)

# 키워드 → 의도 매핑
INTENT_KEYWORDS = {
    "equipment_status": ["상태", "가동", "운전", "정지", "고장", "ERROR", "IDLE", "RUNNING", "MAINTENANCE"],
    "load_rate_query": ["부하율", "부하", "로드율", "load rate", "load"],
    "alert_check": ["알림", "경고", "알럿", "alert", "WARNING", "CRITICAL"],
    "overload_check": ["과부하", "오버로드", "overload", "임계", "초과"],
    "lot_query": ["LOT", "lot", "랏", "랏트", "생산단위", "배치", "Lot"],
}

VALID_INTENTS = {"equipment_status", "load_rate_query", "alert_check", "overload_check", "lot_query", "general_chat"}


def _match_keywords(user_input: str) -> list[str]:
    """키워드 매칭으로 후보 의도를 추출."""
    text = user_input.upper()
    matched = []
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw.upper() in text for kw in keywords):
            matched.append(intent)
    return matched


def _build_context(user_input: str, history: list[dict]) -> str:
    """대화 이력이 있으면 문맥을 포함한 프롬프트 생성."""
    if not history:
        return user_input
    ctx_lines = ["[이전 대화 이력]"]
    for h in history[-5:]:
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
    """의도분석 노드 — 키워드 힌트 + LLM 판단."""
    user_input = state["user_input"]
    history = state.get("conversation_history", [])

    # 1. 키워드 매칭으로 후보 추출
    keyword_hints = _match_keywords(user_input)

    # 2. 대화 맥락 + 키워드 힌트를 LLM에 전달
    prompt_text = _build_context(user_input, history)
    if keyword_hints:
        prompt_text += f"\n\n키워드 힌트: {', '.join(keyword_hints)}"

    response = llm.invoke([
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=prompt_text),
    ])

    # 3. LLM 응답에서 의도 추출 (한 단어)
    raw = response.content.strip().lower().replace("`", "").replace('"', "").strip()
    # 여러 줄이면 첫 줄만
    intent = raw.split("\n")[0].strip()

    # 4. 유효성 검증 — 실패 시 키워드 힌트 폴백
    if intent not in VALID_INTENTS:
        intent = keyword_hints[0] if keyword_hints else "general_chat"

    # 트레이스 로그
    trace = [
        "## Step 1: IntentAgent (키워드+LLM 의도분석)",
        "### State BEFORE",
    ]
    trace += dump_state(state)
    trace += [
        f"### 키워드 매칭",
        f"- 입력: `{user_input}`",
        f"- 매칭된 힌트: `{keyword_hints}`",
        f"### 🔷 FM 입력 (→ {LLM_MODEL})",
        f"- **System**: INTENT_SYSTEM_PROMPT ({len(INTENT_SYSTEM_PROMPT)}자)",
        f"- **Human**:",
        "```",
        prompt_text,
        "```",
        f"### 🔶 FM 출력",
        f"- raw: `{raw}`",
        f"- intent: `{intent}`",
    ]

    updated = dict(state)
    updated["intent"] = intent
    trace += ["### State AFTER"]
    trace += dump_state(updated)

    return {
        "intent": intent,
        "trace_log": state.get("trace_log", []) + trace,
    }
