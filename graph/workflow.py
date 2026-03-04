"""StateGraph 정의 — 노드, 엣지, 조건부 라우팅."""
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from agents.state import AgentState, dump_state
from agents.intent_agent import intent_node
from agents.info_agent import info_node, respond_node
from tools.sql_tools import ALL_TOOLS

_tool_node = ToolNode(ALL_TOOLS)


def tool_node_with_trace(state: AgentState) -> dict:
    """ToolNode 래퍼 — 실행 전후 State 스냅샷을 트레이스에 기록."""
    tool_call_round = state.get("tool_call_round", 0)
    round_label = f" (Round {tool_call_round})" if tool_call_round > 0 else ""
    trace = [
        f"\n---\n## Step 2.5: ToolNode (SQL 실행){round_label}",
        f"### State BEFORE",
    ]
    trace += dump_state(state)

    # 실행할 Tool 정보
    messages = state.get("messages", [])
    last = messages[-1] if messages else None
    if last and hasattr(last, "tool_calls") and last.tool_calls:
        trace.append("### 실행할 Tool")
        for tc in last.tool_calls:
            trace.append(f"- `{tc['name']}({tc['args']})`")

    # 실제 ToolNode 실행
    result = _tool_node.invoke(state)

    # Tool 실행 결과
    new_messages = result.get("messages", [])
    trace.append("### Tool 실행 결과")
    for msg in new_messages:
        content = msg.content[:500] + ("..." if len(msg.content) > 500 else "")
        tool_name = getattr(msg, "name", "unknown")
        trace.append(f"- **ToolMessage** (tool=`{tool_name}`):")
        trace.append(f"  ```\n  {content}\n  ```")

    # State AFTER
    updated = dict(state)
    updated["messages"] = list(state.get("messages", [])) + new_messages
    trace += [f"### State AFTER"]
    trace += dump_state(updated)

    # trace_log를 result에 병합
    result["trace_log"] = state.get("trace_log", []) + trace
    return result


def route_by_intent(state: AgentState) -> str:
    """의도에 따라 info_agent 또는 respond 노드로 라우팅."""
    if state["intent"] == "general_chat":
        return "respond"
    return "info_agent"


def should_use_tools(state: AgentState) -> str:
    """info_agent 출력에 tool_calls가 있으면 tools 노드로, 없으면 respond로."""
    messages = state["messages"]
    last = messages[-1] if messages else None
    if last and hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "respond"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # 노드 등록
    graph.add_node("intent_agent", intent_node)
    graph.add_node("info_agent", info_node)
    graph.add_node("tools", tool_node_with_trace)
    graph.add_node("respond", respond_node)

    # 엣지
    graph.set_entry_point("intent_agent")
    graph.add_conditional_edges("intent_agent", route_by_intent, {
        "info_agent": "info_agent",
        "respond": "respond",
    })
    graph.add_conditional_edges("info_agent", should_use_tools, {
        "tools": "tools",
        "respond": "respond",
    })
    graph.add_edge("tools", "info_agent")
    graph.add_edge("respond", END)

    return graph.compile()
