# 예시 5: 일반 대화 (general_chat)

> **학습 목표**: Tool을 호출하지 않는 **최단 경로**. IntentAgent → ResponseAgent로 직행하며, InfoAgent와 ToolNode를 완전히 건너뛴다. 조건부 라우팅의 핵심 분기점을 보여주는 예시.

---

## 사용자 입력

```
안녕하세요
```

## 에이전트 처리 흐름

```
사용자: "안녕하세요"
  │
  ▼
[Step 1] IntentAgent
  │  intent: "general_chat"
  │  reasoning: "물류 장비 관련 질문이 아닌 일반적인 인사말입니다."
  │
  ▼  intent == "general_chat" → InfoAgent 스킵, ResponseAgent로 직행
[Step 2] ResponseAgent (일반 대화 모드)
  │  Tool 바인딩 없는 별도 LLM 호출
  │  → "안녕하세요! 무엇을 도와드릴까요? 혹시 물류 장비 관리에 대해 궁금한 점이 있으신가요?"
  │
  ▼
사용자에게 응답 출력
```

**전체 2단계** — 다른 예시(4~5단계)와 비교하면 절반 이하의 처리량.

---

## 핵심 설계 포인트

### 1. 조건부 라우팅 — route_intent 함수

```python
# graph/workflow.py
def route_intent(state: AgentState) -> str:
    if state["intent"] == "general_chat":
        return "respond"    # → ResponseAgent로 직행
    return "info_agent"     # → InfoAgent로
```

LangGraph의 `add_conditional_edges`:
```python
graph.add_conditional_edges(
    "intent_agent",
    route_intent,
    {"info_agent": "info_agent", "respond": "respond"},
)
```

**설계 의도**: 일반 대화에 SQL 조회가 불필요. 불필요한 Tool 호출을 방지하여 응답 속도 향상 + 비용 절감.

### 2. ResponseAgent의 이중 경로

```python
# agents/info_agent.py — respond_node
def respond_node(state: AgentState) -> dict:
    if state["intent"] == "general_chat":
        # 경로 A: Tool 바인딩 없는 별도 LLM으로 대화 응답 생성
        response = chat_llm.invoke([...])
        return {"final_answer": response.content, ...}
    else:
        # 경로 B: messages에서 마지막 AI 응답 추출
        ...
```

| 경로 | 진입 조건 | LLM | Tool 바인딩 |
|------|----------|-----|------------|
| A (일반 대화) | `intent == "general_chat"` | 별도 `chat_llm` | 없음 |
| B (정보 조회) | 그 외 모든 intent | 불필요 (이미 생성됨) | — |

**경로 A에서 별도 LLM을 쓰는 이유**: InfoAgent의 LLM은 7개 Tool이 바인딩되어 있어 Tool 호출을 시도할 수 있음.
일반 대화에서는 Tool 호출이 불필요하므로, Tool 바인딩 없는 순수 대화 LLM 사용.

### 3. 일반 대화의 시스템 프롬프트

ResponseAgent의 일반 대화 모드에서는 간단한 프롬프트 적용:

```
"당신은 물류 장비 부하율 관리 시스템의 대화 Agent입니다.
물류와 무관한 질문에는 간단히 답하고, 물류 관련 질문을 유도하세요."
```

**효과**: "오늘 날씨 어때?" 같은 질문에도 답하되, "혹시 물류 장비 관리에 대해 궁금한 점이 있으신가요?"로 자연스럽게 유도.

---

## IntentAgent 출력 상세

```json
{
  "intent": "general_chat",
  "detail": {
    "equipment_type": "",
    "line": "",
    "zone": "",
    "equipment_id": "",
    "hours": 0,
    "keyword": ""
  },
  "reasoning": "물류 장비 관련 질문이 아닌 일반적인 인사말입니다."
}
```

`detail`의 모든 필드가 비어있음 — 추출할 파라미터 자체가 없으므로 당연.

## 최종 응답 (final_answer)

```
안녕하세요! 무엇을 도와드릴까요? 혹시 물류 장비 관리에 대해 궁금한 점이 있으신가요?
```

---

## State 변화 요약

| 단계 | intent | messages 수 | final_answer |
|------|--------|------------|--------------|
| 초기 | `""` | 0 | `""` |
| IntentAgent 후 | `"general_chat"` | 0 | `""` |
| ResponseAgent 후 | `"general_chat"` | 0 | `"안녕하세요! ..."` |

**messages가 끝까지 비어있음**: InfoAgent/ToolNode를 거치지 않았으므로 AIMessage, ToolMessage가 생성되지 않음.

---

## 전체 경로 비교

```
[일반 대화 — 2단계]
IntentAgent → ResponseAgent(경로A)

[정보 조회 — 4~5단계]
IntentAgent → InfoAgent → ToolNode → InfoAgent → ResponseAgent(경로B)
```

| 항목 | 일반 대화 | 정보 조회 |
|------|----------|----------|
| LLM 호출 | 2회 (의도분석 + 대화) | 3회 (의도분석 + Tool선택 + 결과정리) |
| SQL 실행 | 0회 | 1회 이상 |
| messages 사용 | 안 함 | AIMessage, ToolMessage 누적 |
| 평균 응답 시간 | ~1초 | ~3초 |

---

## 학습 포인트

1. **조건부 라우팅**: `route_intent` 함수 하나로 에이전트 흐름이 분기. LangGraph의 `add_conditional_edges`가 StateGraph의 핵심 기능.
2. **불필요한 처리 스킵**: 일반 대화에 SQL Tool을 호출하면 비용 + 지연만 발생. intent 기반 분기로 효율적인 리소스 사용.
3. **LLM 분리**: Tool 바인딩 LLM과 순수 대화 LLM을 분리하여, 각 경로에 최적화된 동작 보장.
4. **도메인 유도**: 일반 대화에서도 "물류 장비 관련 질문을 유도"하여 시스템의 핵심 기능으로 자연스럽게 안내.
