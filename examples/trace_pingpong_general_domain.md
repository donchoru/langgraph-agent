# 예시 13: 핑퐁 대화 — 일반대화 ↔ 도메인(Tool호출) 교차 전환

> **학습 목표**: 5턴에 걸쳐 `general_chat`(Tool 미사용)과 도메인 의도(Tool 호출)가 **번갈아 나오는** 패턴.
> 매 턴마다 FM이 의도를 독립적으로 판단하되, `conversation_history`에 이전 턴의 혼합된 이력(일반+도메인)이 쌓여도
> 현재 질문의 성격에 따라 **정확히 라우팅을 전환**하는 FM I/O를 추적한다.
> Turn 5에서는 **이력 참조형 일반 대화**(대화 요약 요청)를 통해 `ResponseAgent`가 `conversation_history`를 활용하는 패턴을 추가로 검증한다.

---

## 대화 흐름

```
Turn 1: "요즘 날씨 너무 덥다"             ← general_chat (Tool X)
Turn 2: "L1 장비 부하율 어때?"            ← load_rate_query (Tool O)
Turn 3: "점심 뭐 먹지?"                  ← general_chat (Tool X)
Turn 4: "알림 이력 최근꺼 보여줘"          ← alert_check (Tool O)
Turn 5: "지금까지 우리 나눈 대화 요약해줘"  ← general_chat (Tool X, 이력 참조)
```

**핵심 관찰**: 일반 → 도메인 → 일반 → 도메인 → 일반(이력 참조). 매번 경로가 바뀐다.
```
Turn 1: IntentAgent → ResponseAgent                              (FM 2회)
Turn 2: IntentAgent → InfoAgent → ToolNode → InfoAgent → Respond (FM 3회+)
Turn 3: IntentAgent → ResponseAgent                              (FM 2회)
Turn 4: IntentAgent → InfoAgent → ToolNode → InfoAgent → Respond (FM 3회+)
Turn 5: IntentAgent → ResponseAgent (이력 포함)                   (FM 2회)
```

---

## Turn 1: 요즘 날씨 너무 덥다

### IntentAgent

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human**:
```
요즘 날씨 너무 덥다
```
> conversation_history: 0턴 → 이력 없이 질문만 전달

#### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "general_chat",
  "detail": {"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "lot_id": "", "hours": 0, "keyword": ""},
  "reasoning": "물류 장비와 무관한 날씨 관련 일반 대화입니다."
}
```

> **포인트**: "날씨"에 장비, 부하율, 알림, Lot 관련 키워드가 없으므로 `general_chat`으로 분류.

### 라우팅: general_chat → ResponseAgent 직행

```
route_by_intent("general_chat") → "respond_node"
```

> InfoAgent(Tool 루프)를 **완전히 건너뛰고** ResponseAgent로 직행. FM 호출 최소화.

### ResponseAgent (일반대화)

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 일반대화)
- **System**: "당신은 친절한 물류 장비 관리 시스템 어시스턴트입니다. 물류와 무관한 질문에는 간단히 답하고, 물류 관련 질문을 유도하세요." (69자)
- **Human**: "요즘 날씨 너무 덥다"

#### 🔶 FM 출력 (← Gemini)
```
정말 덥죠! 이런 날씨에는 장비 온도 관리도 중요한데요. 혹시 장비 상태나 부하율이 궁금하시면 말씀해주세요! 😊
```

> **포인트**: `temperature=0.7`로 자연스러운 대화 + "물류 관련 질문을 유도하세요" 지시에 따라 장비 질문을 유도.

### 대화 이력 저장
```python
conversation_history = [
    {"user": "요즘 날씨 너무 덥다", "intent": "general_chat",
     "answer": "정말 덥죠! 이런 날씨에는 장비 온도 관리도 중요한데요..."}
]
```

**Turn 1 FM 호출: 2회** (IntentAgent + ResponseAgent)

---

## Turn 2: L1 장비 부하율 어때?

### IntentAgent — ⚡ 핵심: general_chat → 도메인 전환

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human** (conversation_history 포함):
```
[이전 대화 이력]
사용자: 요즘 날씨 너무 덥다
의도: general_chat
응답 요약: 정말 덥죠! 이런 날씨에는 장비 온도 관리도 중요한데요...

[현재 질문]
L1 장비 부하율 어때?

위 대화 이력을 참고하여 현재 질문의 의도를 분석하세요.
'그럼', '거기', '그 설비' 등 대명사는 이전 대화에서 언급된 대상을 참조합니다.
```

> **핵심**: 이전 턴이 `general_chat`이지만, 현재 질문은 "L1 장비 부하율" → 명확한 도메인 질문.
> FM이 이전 이력에 "오염"되지 않고 현재 질문만으로 의도를 판단해야 함.

#### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "load_rate_query",
  "detail": {"line": "L1", "hours": 0},
  "reasoning": "L1 라인의 장비 부하율을 조회하는 요청"
}
```

> **포인트**: `general_chat` → `load_rate_query`로 전환!
> conversation_history에 일반대화 이력이 있지만, FM이 현재 질문의 의도를 독립적으로 판단.

### 라우팅: load_rate_query → InfoAgent

```
route_by_intent("load_rate_query") → "info_agent"
```

### InfoAgent (첫 호출)

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 첫 호출)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 체이닝 규칙, 1781자)
- **Human** (대화 이력 포함):
```
[이전 대화 이력]
- Q: 요즘 날씨 너무 덥다 → intent: general_chat, 응답: 정말 덥죠! 이런 날씨에는...

사용자 질문: L1 장비 부하율 어때?
의도: load_rate_query
상세: {"line": "L1", "hours": 0}

위 의도에 맞는 도구를 호출하여 정보를 조회하세요.
```

> **핵심**: 이전 대화 이력에 `general_chat`이 있지만, InfoAgent는 현재 의도(`load_rate_query`)에 맞는 Tool만 호출.

#### 🔶 FM 출력 (← Gemini) → Tool 호출
- `get_load_rates({'line': 'L1'})`

> **포인트**: 이전 턴의 일반대화와 무관하게 `load_rate_query` 의도에 맞는 Tool 선택.

### ToolNode (SQL 실행)

#### 실행할 Tool
- `get_load_rates({'line': 'L1'})`

#### Tool 실행 결과
```
L1 라인 장비별 최근 부하율:
AGV-L1-CELL-01 | 99.1% | 2025-01-15 10:00
CVR-L1-CELL-01 | 99.8% | 2025-01-15 10:00
CVR-L1-TFT-01  | 72.3% | 2025-01-15 10:00
SHT-L1-MODULE-01 | 45.6% | 2025-01-15 10:00
STK-L1-TFT-01  | 68.9% | 2025-01-15 10:00
```

### InfoAgent 재진입 (Tool 결과 수신)

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 재진입)
- **System**: INFO_SYSTEM_PROMPT (1781자)
- **Messages**: [AIMessage(tool_calls), ToolMessage(부하율 데이터)]
- **Guide**: "도구 실행 결과를 분석하세요. 충분한 정보가 모였으면 최종 응답을 생성하세요."

#### 🔶 FM 출력 (← Gemini) → 텍스트 응답
```
📊 L1 라인 장비 부하율 현황:

| 장비 ID           | 유형     | 구간   | 부하율(%) | 상태  |
|-------------------|----------|--------|-----------|-------|
| CVR-L1-CELL-01    | CONVEYOR | CELL   | 99.8      | ⚠ 과부하 |
| AGV-L1-CELL-01    | AGV      | CELL   | 99.1      | ⚠ 과부하 |
| CVR-L1-TFT-01     | CONVEYOR | TFT    | 72.3      | 정상  |
| STK-L1-TFT-01     | STACKER  | TFT    | 68.9      | 정상  |
| SHT-L1-MODULE-01  | SHUTTLE  | MODULE | 45.6      | 정상  |

⚠ CELL 구간의 2대(CVR, AGV)가 과부하 상태입니다.
```

### 대화 이력 저장
```python
conversation_history = [
    {"user": "요즘 날씨 너무 덥다", "intent": "general_chat", ...},
    {"user": "L1 장비 부하율 어때?", "intent": "load_rate_query",
     "answer": "📊 L1 라인 장비 부하율 현황..."}
]
```

**Turn 2 FM 호출: 3회** (IntentAgent + InfoAgent + InfoAgent 재진입)

---

## Turn 3: 점심 뭐 먹지?

### IntentAgent — ⚡ 핵심: 도메인 → general_chat 복귀

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human** (conversation_history 2턴 포함):
```
[이전 대화 이력]
사용자: 요즘 날씨 너무 덥다
의도: general_chat
응답 요약: 정말 덥죠! 이런 날씨에는 장비 온도 관리도 중요한데요...

사용자: L1 장비 부하율 어때?
의도: load_rate_query
응답 요약: 📊 L1 라인 장비 부하율 현황...

[현재 질문]
점심 뭐 먹지?

위 대화 이력을 참고하여 현재 질문의 의도를 분석하세요.
'그럼', '거기', '그 설비' 등 대명사는 이전 대화에서 언급된 대상을 참조합니다.
```

> **핵심**: conversation_history에 `general_chat` + `load_rate_query` 두 가지 의도가 혼합되어 있음.
> 직전 턴이 `load_rate_query`(도메인)였지만, 현재 질문은 "점심 뭐 먹지?" → 명확한 일반 대화.
> FM이 직전 턴의 도메인 컨텍스트에 끌려가지 않는 것이 핵심.

#### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "general_chat",
  "detail": {"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "lot_id": "", "hours": 0, "keyword": ""},
  "reasoning": "물류 장비와 무관한 점심 메뉴에 대한 일반 대화입니다."
}
```

> **포인트**: `load_rate_query` → `general_chat`으로 전환!
> 직전 턴에 도메인(부하율 조회) 이력이 있지만, FM은 "점심 뭐 먹지?"를 독립적으로 일반 대화로 분류.
> conversation_history의 도메인 이력이 의도 분류를 "오염"시키지 않음.

### 라우팅: general_chat → ResponseAgent 직행

```
route_by_intent("general_chat") → "respond_node"
```

> 다시 InfoAgent를 건너뛰는 **최단 경로**.

### ResponseAgent (일반대화)

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 일반대화)
- **System**: "당신은 친절한 물류 장비 관리 시스템 어시스턴트입니다. 물류와 무관한 질문에는 간단히 답하고, 물류 관련 질문을 유도하세요." (69자)
- **Human**: "점심 뭐 먹지?"

#### 🔶 FM 출력 (← Gemini)
```
더운 날씨엔 냉면이나 냉모밀 어떠세요? 🍜 식사 후에 장비 상태 점검도 잊지 마세요!
```

> **포인트**: 다시 경량 프롬프트(69자)로 전환. temperature=0.7로 자연스러운 답변 + 물류 유도.

### 대화 이력 저장
```python
conversation_history = [
    {"user": "요즘 날씨 너무 덥다", "intent": "general_chat", ...},
    {"user": "L1 장비 부하율 어때?", "intent": "load_rate_query", ...},
    {"user": "점심 뭐 먹지?", "intent": "general_chat",
     "answer": "더운 날씨엔 냉면이나 냉모밀 어떠세요?..."}
]
```

**Turn 3 FM 호출: 2회** (IntentAgent + ResponseAgent)

---

## Turn 4: 알림 이력 최근꺼 보여줘

### IntentAgent — ⚡ 핵심: 다시 도메인으로 전환 (다른 의도)

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human** (conversation_history 3턴 포함):
```
[이전 대화 이력]
사용자: 요즘 날씨 너무 덥다
의도: general_chat
응답 요약: 정말 덥죠! 이런 날씨에는 장비 온도 관리도 중요한데요...

사용자: L1 장비 부하율 어때?
의도: load_rate_query
응답 요약: 📊 L1 라인 장비 부하율 현황...

사용자: 점심 뭐 먹지?
의도: general_chat
응답 요약: 더운 날씨엔 냉면이나 냉모밀 어떠세요?...

[현재 질문]
알림 이력 최근꺼 보여줘

위 대화 이력을 참고하여 현재 질문의 의도를 분석하세요.
'그럼', '거기', '그 설비' 등 대명사는 이전 대화에서 언급된 대상을 참조합니다.
```

> **핵심**: 이력에 general_chat 2회 + load_rate_query 1회가 혼합.
> 직전 턴이 `general_chat`(점심)이었지만, 현재 질문은 "알림 이력" → `alert_check`.
> Turn 2(load_rate_query)와도 다른 새로운 도메인 의도.

#### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "alert_check",
  "detail": {"hours": 0},
  "reasoning": "최근 알림 이력 조회 요청"
}
```

> **포인트**: `general_chat` → `alert_check`으로 전환!
> Turn 2의 `load_rate_query`와는 다른 도메인 의도. FM이 매 턴마다 독립적으로 의도를 판단.

### 라우팅: alert_check → InfoAgent

```
route_by_intent("alert_check") → "info_agent"
```

### InfoAgent (첫 호출)

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 첫 호출)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 체이닝 규칙, 1781자)
- **Human** (대화 이력 3턴 포함):
```
[이전 대화 이력]
- Q: 요즘 날씨 너무 덥다 → intent: general_chat, 응답: 정말 덥죠!...
- Q: L1 장비 부하율 어때? → intent: load_rate_query, 응답: 📊 L1 라인...
- Q: 점심 뭐 먹지? → intent: general_chat, 응답: 더운 날씨엔 냉면이나...

사용자 질문: 알림 이력 최근꺼 보여줘
의도: alert_check
상세: {"hours": 0}

위 의도에 맞는 도구를 호출하여 정보를 조회하세요.
```

> **핵심**: 이전 이력에 general_chat과 load_rate_query가 혼합되어 있지만,
> InfoAgent는 현재 의도(`alert_check`)에 맞는 Tool만 선택.
> Turn 2의 `get_load_rates` Tool을 재호출하지 않음.

#### 🔶 FM 출력 (← Gemini) → Tool 호출
- `get_recent_alerts({})`

> **포인트**: 이력의 혼합 의도와 무관하게, `alert_check` → `get_recent_alerts` 정확한 Tool 매핑.

### ToolNode (SQL 실행)

#### 실행할 Tool
- `get_recent_alerts({})`

#### Tool 실행 결과
```
최근 알림 이력:
CVR-L1-CELL-01 | OVERLOAD | 부하율 99.8% (임계값 95% 초과) | 2025-01-15 09:45
AGV-L1-CELL-01 | OVERLOAD | 부하율 99.1% (임계값 95% 초과) | 2025-01-15 09:30
SHT-L3-CELL-01 | OVERLOAD | 부하율 99.3% (임계값 95% 초과) | 2025-01-15 09:15
CVR-L1-TFT-01  | WARNING  | 부하율 72.3% (임계값 70% 초과) | 2025-01-15 09:00
...
```

### InfoAgent 재진입 (Tool 결과 수신)

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 재진입)
- **System**: INFO_SYSTEM_PROMPT (1781자)
- **Messages**: [AIMessage(tool_calls), ToolMessage(알림 이력 데이터)]
- **Guide**: "도구 실행 결과를 분석하세요. 충분한 정보가 모였으면 최종 응답을 생성하세요."

#### 🔶 FM 출력 (← Gemini) → 텍스트 응답
```
🔔 최근 알림 이력:

| 장비 ID          | 알림 유형 | 내용                          | 시각        |
|------------------|-----------|-------------------------------|-------------|
| CVR-L1-CELL-01   | OVERLOAD  | 부하율 99.8% (임계 95% 초과)  | 09:45       |
| AGV-L1-CELL-01   | OVERLOAD  | 부하율 99.1% (임계 95% 초과)  | 09:30       |
| SHT-L3-CELL-01   | OVERLOAD  | 부하율 99.3% (임계 95% 초과)  | 09:15       |
| CVR-L1-TFT-01    | WARNING   | 부하율 72.3% (임계 70% 초과)  | 09:00       |

⚠ OVERLOAD 알림 3건, WARNING 1건입니다. CELL 구간에 집중되어 있습니다.
```

### 대화 이력 저장
```python
conversation_history = [
    {"user": "요즘 날씨 너무 덥다", "intent": "general_chat", ...},
    {"user": "L1 장비 부하율 어때?", "intent": "load_rate_query", ...},
    {"user": "점심 뭐 먹지?", "intent": "general_chat", ...},
    {"user": "알림 이력 최근꺼 보여줘", "intent": "alert_check",
     "answer": "🔔 최근 알림 이력..."}
]
```

**Turn 4 FM 호출: 3회** (IntentAgent + InfoAgent + InfoAgent 재진입)

---

## Turn 5: 지금까지 우리 나눈 대화 요약해줘

### IntentAgent — ⚡ 핵심: 이력 참조형 일반 대화

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human** (conversation_history 4턴 포함):
```
[이전 대화 이력]
사용자: 요즘 날씨 너무 덥다
의도: general_chat
응답 요약: 정말 덥죠! 이런 날씨에는 장비 온도 관리도 중요한데요...

사용자: L1 장비 부하율 어때?
의도: load_rate_query
응답 요약: 📊 L1 라인 장비 부하율 현황...

사용자: 점심 뭐 먹지?
의도: general_chat
응답 요약: 더운 날씨엔 냉면이나 냉모밀 어떠세요?...

사용자: 알림 이력 최근꺼 보여줘
의도: alert_check
응답 요약: 🔔 최근 알림 이력...

[현재 질문]
지금까지 우리 나눈 대화 요약해줘

위 대화 이력을 참고하여 현재 질문의 의도를 분석하세요.
'그럼', '거기', '그 설비' 등 대명사는 이전 대화에서 언급된 대상을 참조합니다.
```

> **핵심**: "대화 요약" 요청은 장비/부하율/알림/Lot과 무관한 **일반 대화**.
> 단, 이전 이력을 "참조"해야 의미가 있는 질문이므로 IntentAgent에서는 문제없이 `general_chat`으로 분류.
> 진짜 문제는 ResponseAgent가 이력을 받느냐 여부.

#### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "general_chat",
  "detail": {"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "lot_id": "", "hours": 0, "keyword": ""},
  "reasoning": "대화 요약 요청으로 물류 장비 도메인 질문이 아닌 일반 대화입니다."
}
```

### 라우팅: general_chat → ResponseAgent 직행

```
route_by_intent("general_chat") → "respond_node"
```

### ResponseAgent (일반대화 — 이력 참조) — ⚡ 수정 포인트

#### 수정 전 (Bug)
```python
# 수정 전: user_input만 전달 → FM이 이전 대화를 모름
response = simple_llm.invoke([
    SystemMessage(content=chat_system),
    HumanMessage(content=user_input),  # "지금까지 우리 나눈 대화 요약해줘" 단독
])
```
> FM은 이전 대화가 뭔지 전혀 모르므로 "죄송합니다만 이전 대화를 기억하지 못합니다" 같은 응답이 나옴.

#### 수정 후 (Fix)
```python
# 수정 후: conversation_history를 포함하여 전달
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
    HumanMessage(content=human_content),  # 이력 + 현재 질문
])
```

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 일반대화 — 이력 포함)
- **System**: "당신은 친절한 물류 장비 관리 시스템 어시스턴트입니다. 물류와 무관한 질문에는 간단히 답하고, 물류 관련 질문을 유도하세요." (69자)
- **Human** (conversation_history 4턴 포함):
```
[이전 대화 이력]
사용자: 요즘 날씨 너무 덥다
의도: general_chat
응답 요약: 정말 덥죠! 이런 날씨에는 장비 온도 관리도 중요한데요...

사용자: L1 장비 부하율 어때?
의도: load_rate_query
응답 요약: 📊 L1 라인 장비 부하율 현황: CVR-L1-CELL-01 99.8% ⚠ 과부하, AGV-L1-CELL-01 99.1% ⚠ 과부하...

사용자: 점심 뭐 먹지?
의도: general_chat
응답 요약: 더운 날씨엔 냉면이나 냉모밀 어떠세요? 🍜 식사 후에 장비 상태 점검도 잊지 마세요!

사용자: 알림 이력 최근꺼 보여줘
의도: alert_check
응답 요약: 🔔 최근 알림 이력: OVERLOAD 3건(CVR-L1-CELL-01, AGV-L1-CELL-01, SHT-L3-CELL-01), WARNING 1건...

[현재 질문]
지금까지 우리 나눈 대화 요약해줘
```

> **핵심**: IntentAgent의 `_build_context()`와 동일한 패턴으로 이력을 포함.
> FM이 4턴의 대화 맥락을 모두 볼 수 있으므로 정확한 요약이 가능.

#### 🔶 FM 출력 (← Gemini)
```
지금까지 나눈 대화를 정리해드릴게요! 📋

1. 날씨 이야기 — 요즘 날씨가 덥다는 대화를 나눴어요
2. L1 장비 부하율 조회 — CELL 구간의 CVR(99.8%)과 AGV(99.1%)가 과부하 상태였어요 ⚠
3. 점심 메뉴 고민 — 냉면/냉모밀을 추천해드렸죠 🍜
4. 알림 이력 확인 — OVERLOAD 알림 3건, WARNING 1건으로 CELL 구간에 집중되어 있었어요

전반적으로 CELL 구간 장비 과부하가 눈에 띄는데, 추가 점검이 필요하시면 말씀해주세요!
```

> **포인트**: 일반대화(Turn 1, 3)와 도메인 조회(Turn 2, 4) 결과를 **모두 포함**하여 요약.
> `conversation_history` 주입 덕분에 FM이 전체 대화 맥락을 파악.

### 대화 이력 저장
```python
conversation_history = [
    {"user": "요즘 날씨 너무 덥다", "intent": "general_chat", ...},
    {"user": "L1 장비 부하율 어때?", "intent": "load_rate_query", ...},
    {"user": "점심 뭐 먹지?", "intent": "general_chat", ...},
    {"user": "알림 이력 최근꺼 보여줘", "intent": "alert_check", ...},
    {"user": "지금까지 우리 나눈 대화 요약해줘", "intent": "general_chat",
     "answer": "지금까지 나눈 대화를 정리해드릴게요! 📋 1. 날씨 이야기..."}
]
```

**Turn 5 FM 호출: 2회** (IntentAgent + ResponseAgent)

---

## FM 호출 요약 (5턴 전체)

| 턴 | 질문 | 이력 상태 | 의도 | 경로 | FM 호출 |
|----|------|----------|------|------|---------|
| 1 | "요즘 날씨 너무 덥다" | 0턴 | `general_chat` | Intent → **Respond** | **2회** |
| 2 | "L1 장비 부하율 어때?" | 1턴 (general) | `load_rate_query` | Intent → Info → Tool → Info → Respond | **3회** |
| 3 | "점심 뭐 먹지?" | 2턴 (general+domain) | `general_chat` | Intent → **Respond** | **2회** |
| 4 | "알림 이력 최근꺼 보여줘" | 3턴 (mixed) | `alert_check` | Intent → Info → Tool → Info → Respond | **3회** |
| 5 | "지금까지 우리 나눈 대화 요약해줘" | 4턴 (mixed) | `general_chat` | Intent → **Respond (이력 포함)** | **2회** |

**총 FM 호출: 12회** (general_chat 턴은 2회씩, 도메인 턴은 3회씩)

---

## 의도 전환 패턴

```
Turn 1: general_chat      ─── 일반 ───╮
Turn 2: load_rate_query    ─── 도메인 ─╯ ↔ 전환
Turn 3: general_chat       ─── 일반 ───╮
Turn 4: alert_check        ─── 도메인 ─╯ ↔ 전환
Turn 5: general_chat       ─── 일반 (이력 참조) ── 마무리
```

> 도메인 전환도 2가지: Turn 2는 `load_rate_query`, Turn 4는 `alert_check`.
> 같은 도메인으로 돌아가는 게 아니라 **다른 의도**로 돌아감.
> Turn 5는 같은 `general_chat`이지만 Turn 1, 3과 성격이 다름 — **이력 참조가 필수**인 일반 대화.

---

## conversation_history 누적 변화

| 턴 | history 내용 | FM 입력 토큰 영향 |
|----|-------------|------------------|
| 1 | (없음) | 최소 |
| 2 | `[general_chat]` | 이력 1건 추가 |
| 3 | `[general_chat, load_rate_query]` | 이력 2건 (도메인 응답은 길어서 토큰 증가) |
| 4 | `[general_chat, load_rate_query, general_chat]` | 이력 3건 (혼합) |
| 5 | `[general_chat, load_rate_query, general_chat, alert_check]` | 이력 4건 (혼합, ResponseAgent도 이력 수신) |

> 이력이 쌓일수록 FM 입력 토큰이 증가하지만, `_build_context()`가 응답을 150자로 잘라서 제한.
> Turn 5부터는 ResponseAgent도 동일한 이력 포맷을 사용하므로 IntentAgent와 토큰 사용량이 유사.

---

## 학습 포인트

1. **핑퐁 라우팅 전환**: `general_chat`은 InfoAgent를 건너뛰는 최단 경로(FM 2회), 도메인 의도는 InfoAgent+ToolNode 경유(FM 3회+). 매 턴마다 그래프 경로가 다르게 선택됨. LangGraph의 `conditional_edges`가 이 분기를 담당.

2. **혼합 이력에서 의도 독립 판단**: conversation_history에 `general_chat`과 도메인 의도가 뒤섞여 있어도, FM은 현재 질문만으로 의도를 정확히 분류. "이전 대화를 **참고**하되, 현재 질문의 의도를 분석하세요"라는 프롬프트 설계가 핵심.

3. **도메인 의도도 매번 다름**: Turn 2는 `load_rate_query`(부하율), Turn 4는 `alert_check`(알림). 같은 도메인이라도 서로 다른 의도 → 다른 Tool 호출. FM이 이전 도메인 턴의 Tool을 재활용하지 않음.

4. **System 프롬프트 전환**: general_chat 턴에서는 경량 프롬프트(69자, temperature=0.7), 도메인 턴에서는 INFO_SYSTEM_PROMPT(1781자, temperature=0). 프롬프트와 temperature가 의도에 따라 동적으로 바뀜.

5. **messages 리셋 vs history 유지**: `messages`(Tool 호출 히스토리)는 매 턴 리셋되어 이전 턴의 Tool 결과가 유출되지 않음. 반면 `conversation_history`는 턴마다 누적되어 FM의 문맥 참고용으로 제공. 이 두 가지 분리가 핑퐁 전환을 깔끔하게 만드는 설계.

6. **토큰 비용 패턴**: general_chat 턴은 FM 2회(경량), 도메인 턴은 FM 3회(중량). 5턴 기준 총 12회 호출. 일반대화가 많을수록 비용 절약, 도메인 질문이 많을수록 비용 증가. 실제 운영에서는 이 비율이 비용 예측에 중요.

7. **이력 참조형 일반 대화 (Turn 5에서 발견한 버그와 수정)**: `general_chat`이라도 "대화 요약해줘", "아까 뭐라고 했지?" 같은 **이력 참조가 필요한 질문**이 존재. 수정 전 `respond_node`는 `user_input`만 FM에 전달하여 이런 질문에 답할 수 없었음. `IntentAgent._build_context()`와 동일한 패턴으로 `conversation_history`를 `ResponseAgent`에도 주입하여 해결. 같은 의도(`general_chat`)라도 **단발성**(날씨, 점심)과 **이력 참조형**(요약, 아까 뭐라고 했지?)으로 성격이 다를 수 있다는 교훈.
