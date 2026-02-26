"""메시지 히스토리 토큰 관리 — ToolMessage 비대화 방지.

문제: InfoAgent ↔ ToolNode 루프가 반복되면 messages가 계속 쌓인다.
     특히 ToolMessage(SQL 결과 JSON)가 수백~수천 행이면 LLM 토큰 한도 초과.

전략:
  1. ToolMessage 개별 트리밍: 결과가 MAX_TOOL_RESULT_CHARS를 넘으면 잘라냄
  2. 히스토리 윈도우: messages가 MAX_MESSAGES를 넘으면 오래된 것부터 제거
  3. 잘린 데이터에는 "[...truncated]" 마커 추가 → LLM이 데이터가 잘렸음을 인지

Gemini 2.0 Flash 기준:
  - 컨텍스트: 1M tokens (여유 있지만, 응답 품질 + 비용 + 속도를 위해 제한)
  - 한글 1자 ≈ 2~3 tokens → 3000자 ≈ 6000~9000 tokens
"""

from copy import deepcopy
from langchain_core.messages import BaseMessage, ToolMessage, AIMessage

# ── 설정값 ────────────────────────────────────────────────
MAX_TOOL_RESULT_CHARS = 3000    # ToolMessage 1개당 최대 문자 수
MAX_MESSAGES = 12               # 히스토리에 유지할 최대 메시지 수
MAX_TOTAL_CHARS = 30000         # 전체 메시지 합산 최대 문자 수
# ──────────────────────────────────────────────────────────


def _estimate_chars(messages: list[BaseMessage]) -> int:
    """메시지 리스트의 총 문자 수 추정."""
    return sum(len(getattr(m, "content", "") or "") for m in messages)


def _truncate_content(content: str, max_chars: int) -> str:
    """문자열이 max_chars를 초과하면 잘라내고 마커 추가."""
    if len(content) <= max_chars:
        return content
    # JSON 배열이면 앞부분만 남기고 닫아줌
    truncated = content[:max_chars]
    return truncated + f"\n\n[...truncated: 원본 {len(content):,}자 중 {max_chars:,}자만 표시]"


def trim_tool_messages(messages: list[BaseMessage]) -> list[BaseMessage]:
    """ToolMessage의 content가 너무 크면 잘라낸다.

    원본을 변경하지 않고 새 리스트를 반환.

    Args:
        messages: LangGraph State의 messages 리스트

    Returns:
        트리밍된 messages 복사본
    """
    result = []
    for msg in messages:
        if isinstance(msg, ToolMessage) and len(msg.content or "") > MAX_TOOL_RESULT_CHARS:
            trimmed = deepcopy(msg)
            trimmed.content = _truncate_content(msg.content, MAX_TOOL_RESULT_CHARS)
            result.append(trimmed)
        else:
            result.append(msg)
    return result


def trim_history(messages: list[BaseMessage]) -> list[BaseMessage]:
    """메시지 히스토리가 너무 길면 오래된 것부터 제거.

    규칙:
      1. MAX_MESSAGES 초과 시 → 최근 MAX_MESSAGES개만 유지
      2. 단, 첫 번째 AIMessage(tool_calls)는 보존 (컨텍스트 유지)
      3. MAX_TOTAL_CHARS 초과 시 → 가장 오래된 ToolMessage부터 요약

    Args:
        messages: ToolMessage 트리밍이 완료된 messages 리스트

    Returns:
        윈도우 적용된 messages
    """
    if len(messages) <= MAX_MESSAGES and _estimate_chars(messages) <= MAX_TOTAL_CHARS:
        return messages

    # 메시지 수 초과 → 최근 것만 유지
    if len(messages) > MAX_MESSAGES:
        # 첫 AIMessage(tool_calls)가 있으면 보존
        first_ai = None
        for i, msg in enumerate(messages):
            if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
                first_ai = (i, msg)
                break

        trimmed = messages[-MAX_MESSAGES:]

        # 첫 AIMessage가 잘렸으면 맨 앞에 복원
        if first_ai and first_ai[1] not in trimmed:
            trimmed = [first_ai[1]] + trimmed[-(MAX_MESSAGES - 1):]

        messages = trimmed

    # 총 문자 수 초과 → 가장 긴 ToolMessage부터 추가 트리밍
    while _estimate_chars(messages) > MAX_TOTAL_CHARS:
        longest_idx = -1
        longest_len = 0
        for i, msg in enumerate(messages):
            if isinstance(msg, ToolMessage):
                content_len = len(msg.content or "")
                if content_len > longest_len:
                    longest_len = content_len
                    longest_idx = i

        if longest_idx == -1 or longest_len <= 500:
            break  # 더 이상 줄일 ToolMessage가 없음

        # 가장 긴 ToolMessage를 절반으로 줄임
        msg = messages[longest_idx]
        new_max = max(500, longest_len // 2)
        trimmed_msg = deepcopy(msg)
        trimmed_msg.content = _truncate_content(msg.content, new_max)
        messages = messages[:longest_idx] + [trimmed_msg] + messages[longest_idx + 1:]

    return messages


def prepare_messages(messages: list[BaseMessage]) -> list[BaseMessage]:
    """LLM 호출 전 메시지를 정리하는 통합 함수.

    사용법:
        llm_messages = [SystemMessage(...)] + prepare_messages(state["messages"])

    처리 순서:
        1. ToolMessage 개별 트리밍 (MAX_TOOL_RESULT_CHARS)
        2. 히스토리 윈도우 적용 (MAX_MESSAGES, MAX_TOTAL_CHARS)
    """
    trimmed = trim_tool_messages(messages)
    windowed = trim_history(trimmed)
    return windowed
