from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, ToolMessage


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    intent: str            # 분류된 의도
    intent_detail: str     # 의도 상세 (JSON 문자열)
    trace_log: list[str]   # 트레이스 로그 라인
    user_input: str        # 원본 사용자 입력
    final_answer: str      # 최종 응답
    conversation_history: list[dict]  # 이전 턴 이력 [{"user": "...", "answer": "...", "intent": "..."}]
    tool_call_round: int   # 도구 호출 라운드 카운터 (무한 루프 방지, 기본 0)


def _fmt_message(msg: BaseMessage) -> str:
    """메시지 한 건을 읽기 좋은 문자열로 변환."""
    if isinstance(msg, HumanMessage):
        tag = "HumanMessage"
    elif isinstance(msg, AIMessage):
        tag = "AIMessage"
        if msg.tool_calls:
            calls = ", ".join(f"{tc['name']}({tc['args']})" for tc in msg.tool_calls)
            return f"  - **{tag}** [tool_calls]: `{calls}`"
        content = msg.content[:300] + ("..." if len(msg.content) > 300 else "")
        return f"  - **{tag}**: {content}"
    elif isinstance(msg, ToolMessage):
        tag = "ToolMessage"
        content = msg.content[:300] + ("..." if len(msg.content) > 300 else "")
        return f"  - **{tag}** (tool=`{msg.name}`): `{content}`"
    else:
        tag = type(msg).__name__
    content = msg.content[:300] + ("..." if len(msg.content) > 300 else "")
    return f"  - **{tag}**: {content}"


def dump_state(state: AgentState) -> list[str]:
    """현재 AgentState 전체를 트레이스용 Markdown 라인 리스트로 변환."""
    history = state.get("conversation_history", [])
    lines = [
        "### State Snapshot",
        f"- **user_input**: `{state.get('user_input', '')}`",
        f"- **intent**: `{state.get('intent', '')}`",
        f"- **intent_detail**: `{state.get('intent_detail', '')}`",
        f"- **final_answer**: `{(state.get('final_answer', '') or '')[:200]}`",
        f"- **conversation_history** ({len(history)}턴):",
    ]
    for h in history[-3:]:  # 최근 3턴만 표시
        lines.append(f"  - Q: `{h.get('user', '')}` → A: `{h.get('answer', '')[:80]}...` ({h.get('intent', '')})")
    lines.append(f"- **messages** ({len(state.get('messages', []))}건):")
    for msg in state.get("messages", []):
        lines.append(_fmt_message(msg))
    return lines
