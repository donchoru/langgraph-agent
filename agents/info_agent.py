"""정보조회 Agent — 의도 기반으로 Tool 호출 후 응답 생성."""
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.state import AgentState, dump_state
from agents.prompts import INFO_SYSTEM_PROMPT
from tools.sql_tools import ALL_TOOLS
from config import GEMINI_API_KEY, GEMINI_MODEL


llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0,
).bind_tools(ALL_TOOLS)


def info_node(state: AgentState) -> dict:
    """정보조회 노드 — Tool 호출을 위한 LLM 호출.
    첫 호출: 시스템+사용자 프롬프트로 tool 호출 유도.
    재진입(tool 결과 반환 후): 전체 메시지 히스토리를 전달하여 최종 응답 생성.
    """
    intent = state["intent"]
    intent_detail = state["intent_detail"]
    user_input = state["user_input"]
    messages = state.get("messages", [])

    reentry = bool(messages)
    step_label = "InfoAgent 재진입 (Tool 결과 수신)" if reentry else "InfoAgent (정보조회)"

    trace = [
        f"\n---\n## Step 2: {step_label}",
        f"### State BEFORE",
    ]
    trace += dump_state(state)

    # 이미 메시지가 있으면 (tool 결과 포함) 전체 히스토리로 호출
    if reentry:
        llm_messages = [SystemMessage(content=INFO_SYSTEM_PROMPT)] + list(messages)
        trace.append(f"### LLM 호출 (메시지 히스토리 {len(messages)}건 포함)")
    else:
        prompt = (
            f"사용자 질문: {user_input}\n"
            f"의도: {intent}\n"
            f"상세: {intent_detail}\n\n"
            f"위 의도에 맞는 도구를 호출하여 정보를 조회하세요."
        )
        llm_messages = [
            SystemMessage(content=INFO_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
        trace.append(f"### LLM 호출 (첫 호출)")

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

    if response.tool_calls:
        trace.append("### LLM 출력 → Tool 호출 요청")
        for tc in response.tool_calls:
            trace.append(f"- `{tc['name']}({tc['args']})`")
        trace.append(f"### 다음: ToolNode로 이동")
    else:
        trace.append(f"### LLM 출력 → 텍스트 응답")
        trace.append(f"```\n{response.content[:500]}\n```")
        trace.append(f"### 다음: ResponseAgent로 이동")

    # State AFTER 스냅샷
    updated = dict(state)
    updated_msgs = list(state.get("messages", [])) + [response]
    updated["messages"] = updated_msgs
    trace += [f"### State AFTER"]
    trace += dump_state(updated)

    return {
        "messages": [response],
        "trace_log": state.get("trace_log", []) + trace,
    }


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
        # 일반 대화 — 간단히 응답
        simple_llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0.7,
        )
        response = simple_llm.invoke([
            SystemMessage(content="당신은 친절한 물류 장비 관리 시스템 어시스턴트입니다. 물류와 무관한 질문에는 간단히 답하고, 물류 관련 질문을 유도하세요."),
            HumanMessage(content=user_input),
        ])
        answer = response.content
        trace.append(f"### 처리: 일반 대화 LLM 직접 호출")
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
        trace.append(f"### 처리: 메시지 히스토리에서 최종 AI 응답 추출")

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
