"""StateGraph 정의 — 노드, 엣지, 조건부 라우팅."""
from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.intent_agent import intent_node
from agents.info_agent import react_agent_node, respond_node


def route_by_intent(state: AgentState) -> str:
    """의도에 따라 react_agent 또는 respond 노드로 라우팅."""
    if state["intent"] == "general_chat":
        return "respond"
    return "react_agent"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # 노드 등록
    graph.add_node("intent_agent", intent_node)
    graph.add_node("react_agent", react_agent_node)
    graph.add_node("respond", respond_node)

    # 엣지
    graph.set_entry_point("intent_agent")
    graph.add_conditional_edges("intent_agent", route_by_intent, {
        "react_agent": "react_agent",
        "respond": "respond",
    })
    graph.add_edge("react_agent", "respond")
    graph.add_edge("respond", END)

    return graph.compile()
