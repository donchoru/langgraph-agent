"""정보조회 Agent — create_react_agent 기반 도구 호출 + 응답 생성."""
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from agents.state import AgentState, dump_state
from agents.prompts import INFO_SYSTEM_PROMPT
from agents.message_trimmer import prepare_messages
from tools.sql_tools import ALL_TOOLS
from config import LLM_MODEL
from llm_factory import create_llm


def _prompt(state):
    """create_react_agent의 prompt — 시스템 프롬프트 + 메시지 트리밍."""
    messages = state["messages"]
    trimmed = prepare_messages(list(messages))
    return [SystemMessage(content=INFO_SYSTEM_PROMPT)] + trimmed


# ReAct Agent 생성
_llm = create_llm(temperature=0)
react_agent = create_react_agent(_llm, ALL_TOOLS, prompt=_prompt)


def react_agent_node(state: AgentState) -> dict:
    """ReAct Agent 노드 — create_react_agent로 도구 호출 + 응답 생성."""
    user_input = state["user_input"]
    intent = state["intent"]
    history = state.get("conversation_history", [])

    # 대화 이력이 있으면 문맥 포함
    history_ctx = ""
    if history:
        ctx_lines = ["[이전 대화 이력]"]
        for h in history[-3:]:
            ctx_lines.append(f"- Q: {h['user']} → intent: {h.get('intent', '')}, 응답: {h.get('answer', '')[:200]}")
        history_ctx = "\n".join(ctx_lines) + "\n\n"

    prompt = (
        f"{history_ctx}"
        f"사용자 질문: {user_input}\n"
        f"의도: {intent}\n\n"
        f"위 의도에 맞는 도구를 호출하여 정보를 조회하세요."
    )

    # Trace BEFORE
    trace = [
        "\n---\n## Step 2: ReAct Agent (정보조회 + 도구 호출)",
        "### State BEFORE",
    ]
    trace += dump_state(state)
    trace += [
        f"### 🔷 FM 입력 (→ {LLM_MODEL}, ReAct Agent)",
        f"- **System**: INFO_SYSTEM_PROMPT ({len(INFO_SYSTEM_PROMPT)}자)",
        f"- **Human**:",
        "```",
        prompt,
        "```",
    ]

    try:
        result = react_agent.invoke(
            {"messages": [HumanMessage(content=prompt)]},
            config={"recursion_limit": 10},
        )
        react_messages = result["messages"]
    except Exception as e:
        error_msg = f"ReAct Agent 호출 실패: {type(e).__name__}: {e}"
        trace.append(f"### ERROR\n- `{error_msg}`")
        fallback = AIMessage(content="죄송합니다. 정보 조회 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
        return {
            "messages": [fallback],
            "trace_log": state.get("trace_log", []) + trace,
        }

    # Trace: ReAct Agent 실행 로그
    trace.append("### ReAct Agent 실행 로그")
    for msg in react_messages:
        if isinstance(msg, HumanMessage):
            trace.append(f"- **HumanMessage**: {msg.content[:200]}")
        elif isinstance(msg, AIMessage):
            if msg.tool_calls:
                calls = ", ".join(f"{tc['name']}({tc['args']})" for tc in msg.tool_calls)
                trace.append(f"- **AIMessage** [tool_calls]: `{calls}`")
            else:
                trace.append(f"- **🔶 AIMessage (최종 응답)**: {msg.content[:300]}")
        elif isinstance(msg, ToolMessage):
            trace.append(f"- **ToolMessage** (tool=`{msg.name}`): `{msg.content[:300]}`")

    # State AFTER
    updated = dict(state)
    updated["messages"] = list(state.get("messages", [])) + react_messages
    trace += ["### State AFTER"]
    trace += dump_state(updated)

    return {
        "messages": react_messages,
        "trace_log": state.get("trace_log", []) + trace,
    }


def respond_node(state: AgentState) -> dict:
    """응답 생성 노드 — 일반 대화이거나 ReAct Agent 결과에서 최종 응답 추출."""
    intent = state["intent"]
    messages = state["messages"]
    user_input = state["user_input"]

    step_num = "2" if intent == "general_chat" else "3"
    trace = [
        f"\n---\n## Step {step_num}: ResponseAgent (응답생성)",
        "### State BEFORE",
    ]
    trace += dump_state(state)

    if intent == "general_chat":
        # 일반 대화 — 대화 이력 포함하여 응답
        chat_system = "당신은 친절한 물류 장비 관리 시스템 어시스턴트입니다. 물류와 무관한 질문에는 간단히 답하고, 물류 관련 질문을 유도하세요."
        simple_llm = create_llm(temperature=0.7)

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
            "```",
            human_content,
            "```",
            f"### 🔶 FM 출력",
            "```",
            answer,
            "```",
        ]
    else:
        # ReAct Agent 결과에서 마지막 AI 텍스트 응답 추출
        last_ai = None
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                last_ai = msg
                break

        if last_ai and last_ai.content:
            answer = last_ai.content
        else:
            answer = "조회 결과를 처리하지 못했습니다. 다시 시도해주세요."
        trace.append("### 처리: ReAct Agent에서 생성된 최종 AI 응답 추출")

    trace += [
        "### 최종 응답 (final_answer)",
        f"```\n{answer}\n```",
    ]

    updated = dict(state)
    updated["final_answer"] = answer
    trace += ["### State AFTER"]
    trace += dump_state(updated)

    return {
        "final_answer": answer,
        "trace_log": state.get("trace_log", []) + trace,
    }
