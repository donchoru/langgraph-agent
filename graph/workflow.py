"""StateGraph 정의 — 노드, 엣지, 조건부 라우팅."""
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from agents.state import AgentState
from agents.intent_agent import intent_node
from agents.info_agent import info_node, respond_node
from tools.sql_tools import ALL_TOOLS


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
    graph.add_node("tools", ToolNode(ALL_TOOLS))
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
