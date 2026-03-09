"""정보조회 Agent — 의도 기반으로 Tool 호출 후 응답 생성."""
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from agents.state import AgentState, dump_state
from agents.prompts import INFO_SYSTEM_PROMPT
from agents.message_trimmer import prepare_messages
from tools.sql_tools import ALL_TOOLS
from config import LLM_MODEL
from llm_factory import create_llm

MAX_TOOL_ROUNDS = 3

llm = create_llm(temperature=0, bind_tools=ALL_TOOLS)


def info_node(state: AgentState) -> dict:
    """정보조회 노드 — Tool 호출을 위한 LLM 호출.
    첫 호출: 시스템+사용자 프롬프트로 tool 호출 유도.
    재진입(tool 결과 반환 후): 결과 분석 → 추가 도구 호출 또는 최종 응답 생성.
    """
    intent = state["intent"]
    intent_detail = state["intent_detail"]
    user_input = state["user_input"]
    messages = state.get("messages", [])
    tool_call_round = state.get("tool_call_round", 0)

    reentry = bool(messages)
    round_label = f" (Round {tool_call_round})" if reentry else ""
    step_label = f"InfoAgent 재진입 (Tool 결과 수신){round_label}" if reentry else "InfoAgent (정보조회)"

    trace = [
        f"\n---\n## Step 2: {step_label}",
        f"### State BEFORE",
    ]
    trace += dump_state(state)

    # 이미 메시지가 있으면 (tool 결과 포함) 트리밍 후 히스토리로 호출
    if reentry:
        trimmed = prepare_messages(list(messages))

        # 라운드 제한에 따라 지시 메시지 추가
        if tool_call_round < MAX_TOOL_ROUNDS:
            guide_msg = HumanMessage(content=(
                "도구 실행 결과를 분석하세요. "
                "사용자의 질문에 완전히 답하기 위해 추가 조회가 필요하면 도구를 더 호출하고, "
                "충분한 정보가 모였으면 최종 응답을 생성하세요."
            ))
        else:
            guide_msg = HumanMessage(content=(
                "더 이상 도구를 호출하지 말고 현재까지의 결과로 최종 응답을 생성하세요."
            ))

        llm_messages = [SystemMessage(content=INFO_SYSTEM_PROMPT)] + trimmed + [guide_msg]
        trim_note = (f"원본 {len(messages)}건 → 트리밍 {len(trimmed)}건"
                     if len(trimmed) < len(messages)
                     else f"메시지 히스토리 {len(messages)}건 포함")
        trace += [
            f"### 🔷 FM 입력 (→ {LLM_MODEL}, 재진입 Round {tool_call_round})",
            f"- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 체이닝 규칙, {len(INFO_SYSTEM_PROMPT)}자)",
            f"- **Messages**: {trim_note}",
            f"- **Guide**: \"{guide_msg.content}\"",
        ]
        # 메시지 요약 (마지막 3건)
        for m in trimmed[-3:]:
            role = type(m).__name__
            content_preview = str(getattr(m, 'content', ''))[:200]
            trace.append(f"  - `{role}`: {content_preview}")
    else:
        # 대화 이력이 있으면 문맥 포함
        history = state.get("conversation_history", [])
        history_ctx = ""
        if history:
            ctx_lines = ["[이전 대화 이력]"]
            for h in history[-3:]:
                ctx_lines.append(f"- Q: {h['user']} → intent: {h.get('intent', '')}, 응답: {h.get('answer', '')[:200]}")
            history_ctx = "\n".join(ctx_lines) + "\n\n"

        prompt = (
            f"{history_ctx}"
            f"사용자 질문: {user_input}\n"
            f"의도: {intent}\n"
            f"상세: {intent_detail}\n\n"
            f"위 의도에 맞는 도구를 호출하여 정보를 조회하세요."
        )
        llm_messages = [
            SystemMessage(content=INFO_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
        trace += [
            f"### 🔷 FM 입력 (→ {LLM_MODEL}, 첫 호출)",
            f"- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 체이닝 규칙, {len(INFO_SYSTEM_PROMPT)}자)",
            f"- **Human**:",
            f"```",
            f"{prompt}",
            f"```",
        ]

    try:
        response = llm.invoke(llm_messages)
    except Exception as e:
        error_msg = f"LLM 호출 실패: {type(e).__name__}: {e}"
        trace.append(f"### ERROR\n- `{error_msg}`")
        fallback = AIMessage(content="죄송합니다. 정보 조회 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
        return {
            "messages": [fallback],
            "trace_log": state.get("trace_log", []) + trace,
        }

    result = {
        "messages": [response],
        "trace_log": state.get("trace_log", []) + trace,
    }

    if response.tool_calls:
        trace += [
            f"### 🔶 FM 출력 → Tool 호출 요청 (Round {tool_call_round + 1})",
        ]
        for tc in response.tool_calls:
            trace.append(f"- `{tc['name']}({tc['args']})`")
        trace.append(f"### 다음: ToolNode로 이동")
        result["tool_call_round"] = tool_call_round + 1
    else:
        trace += [
            f"### 🔶 FM 출력 → 텍스트 응답",
            f"```",
            f"{response.content[:500]}",
            f"```",
            f"### 다음: ResponseAgent로 이동",
        ]

    # State AFTER 스냅샷
    updated = dict(state)
    updated_msgs = list(state.get("messages", [])) + [response]
    updated["messages"] = updated_msgs
    trace += [f"### State AFTER"]
    trace += dump_state(updated)

    result["trace_log"] = state.get("trace_log", []) + trace
    return result


def respond_node(state: AgentState) -> dict:
    """응답 생성 노드 — 일반 대화이거나 Tool 결과 정리 후 최종 응답."""
    intent = state["intent"]
    messages = state["messages"]
    user_input = state["user_input"]

    step_num = "2" if intent == "general_chat" else "3"
    trace = [
        f"\n---\n## Step {step_num}: ResponseAgent (응답생성)",
        f"### State BEFORE",
    ]
    trace += dump_state(state)

    if intent == "general_chat":
        # 일반 대화 — 대화 이력 포함하여 응답
        chat_system = "당신은 친절한 물류 장비 관리 시스템 어시스턴트입니다. 물류와 무관한 질문에는 간단히 답하고, 물류 관련 질문을 유도하세요."
        simple_llm = create_llm(temperature=0.7)

        # 대화 이력이 있으면 문맥 포함 (요약, 대명사 참조 등 대응)
        history = state.get("conversation_history", [])
        if history:
            ctx_lines = ["[이전 대화 이력]"]
            for h in history[-5:]:
                ctx_lines.append(f"사용자: {h['user']}")
                ctx_lines.append(f"의도: {h.get('intent', '')}")
                ctx_lines.append(f"응답 요약: {h.get('answer', '')[:150]}")
                ctx_lines.append("")
            ctx_lines.append(f"[현재 질문]\n{user_input}")
            human_content = "\n".join(ctx_lines)
        else:
            human_content = user_input

        response = simple_llm.invoke([
            SystemMessage(content=chat_system),
            HumanMessage(content=human_content),
        ])
        answer = response.content
        trace += [
            f"### 🔷 FM 입력 (→ {LLM_MODEL}, 일반대화)",
            f"- **System**: \"{chat_system[:80]}...\" ({len(chat_system)}자)",
            f"- **Human**:",
            f"```",
            f"{human_content}",
            f"```",
            f"### 🔶 FM 출력",
            f"```",
            f"{answer}",
            f"```",
        ]
    else:
        # Tool 결과가 포함된 메시지에서 마지막 AI 응답 추출
        last_ai = None
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                last_ai = msg
                break

        if last_ai and last_ai.content:
            answer = last_ai.content
        else:
            answer = "조회 결과를 처리하지 못했습니다. 다시 시도해주세요."
        trace.append(f"### 처리: InfoAgent 재진입에서 생성된 최종 AI 응답 추출")

    trace += [
        f"### 최종 응답 (final_answer)",
        f"```\n{answer}\n```",
    ]

    # State AFTER
    updated = dict(state)
    updated["final_answer"] = answer
    trace += [f"### State AFTER"]
    trace += dump_state(updated)

    return {
        "final_answer": answer,
        "trace_log": state.get("trace_log", []) + trace,
    }
