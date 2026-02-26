from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    intent: str            # 분류된 의도
    intent_detail: str     # 의도 상세 (JSON 문자열)
    trace_log: list[str]   # 트레이스 로그 라인
    user_input: str        # 원본 사용자 입력
    final_answer: str      # 최종 응답
