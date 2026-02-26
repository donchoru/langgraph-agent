# 예시 10: 멀티턴 토픽 전환 — Lot 질문 후 장비 상태 질문 (intent 완전 변경)

> **학습 목표**: 멀티턴 대화에서 **완전히 다른 주제**로 전환했을 때 시스템이 어떻게 반응하는지.
> `conversation_history`에 이전 토픽이 남아있지만, IntentAgent가 새 의도를 올바르게 분류하는 과정을 추적한다.

---

## 대화 흐름

```
Turn 1: "CVR-L1-TFT-01에 Lot 뭐 있어?"    ← lot_query
Turn 2: "L2 장비 상태 어때?"                ← equipment_status (완전 토픽 전환)
```

---

## Turn 1: CVR-L1-TFT-01에 Lot 뭐 있어?

### IntentAgent

```
State BEFORE:
  user_input: "CVR-L1-TFT-01에 Lot 뭐 있어?"
  conversation_history: 0턴
  intent: ""

LLM 출력:
  intent: "lot_query"
  detail: {"equipment_id":"CVR-L1-TFT-01","lot_id":""}
```

### InfoAgent → ToolNode (2개 Tool 동시 호출)

```
tool_calls: [
  get_lots_on_equipment({"equipment_id":"CVR-L1-TFT-01"}),
  get_lots_scheduled_for_equipment({"equipment_id":"CVR-L1-TFT-01"})
]

ToolMessage 1 (get_lots_on_equipment):
  [
    {"lot_id":"LOT-020","status":"IN_PROCESS","current_equipment_id":"CVR-L1-TFT-01"},
    {"lot_id":"LOT-023","status":"IN_PROCESS","current_equipment_id":"CVR-L1-TFT-01"}
  ]

ToolMessage 2 (get_lots_scheduled_for_equipment):
  [
    {"lot_id":"LOT-020","scheduled_equipment_id":"CVR-L1-TFT-01","current_equipment_id":"CVR-L1-TFT-01"},
    {"lot_id":"LOT-023","scheduled_equipment_id":"CVR-L1-TFT-01","current_equipment_id":"CVR-L1-TFT-01"},
    {"lot_id":"LOT-005","scheduled_equipment_id":"CVR-L1-TFT-01","current_equipment_id":"AGV-L1-CELL-01"},
    ... (총 6건)
  ]
```

### ResponseAgent

```
final_answer:
  📍 CVR-L1-TFT-01에 현재 물리적으로 있는 Lot:
  | LOT-020 | OLED_B | 206 | IN_PROCESS |
  | LOT-023 | OLED_A | 289 | IN_PROCESS |

  📅 CVR-L1-TFT-01에 예정된 Lot:
  | LOT-020 | ... | CVR-L1-TFT-01 |
  | LOT-005 | ... | ⚡ 이동 중 (AGV-L1-CELL-01) |
  | ...
```

### 대화 이력 저장

```python
conversation_history = [
    {"user": "CVR-L1-TFT-01에 Lot 뭐 있어?", "intent": "lot_query",
     "answer": "📍 CVR-L1-TFT-01에 현재 물리적으로 있는 Lot..."}
]
```

---

## Turn 2: L2 장비 상태 어때?

### IntentAgent — ⚡ 핵심: 토픽 전환 감지

```
State BEFORE:
  user_input: "L2 장비 상태 어때?"
  conversation_history: 1턴
    - Q: "CVR-L1-TFT-01에 Lot 뭐 있어?" → lot_query

LLM 입력:
  [이전 대화 이력]
  사용자: CVR-L1-TFT-01에 Lot 뭐 있어?
  의도: lot_query
  응답 요약: 📍 CVR-L1-TFT-01에 현재 물리적으로 있는 Lot...

  [현재 질문]
  L2 장비 상태 어때?

LLM 출력:
  intent: "equipment_status"     ← lot_query → equipment_status 전환!
  detail: {"line":"L2"}
  reasoning: "L2 라인의 장비 상태를 요청하고 있음"
```

**포인트**: 이전 턴이 `lot_query`였지만, "L2 장비 상태 어때?"는 명확한 `equipment_status`.
LLM이 `conversation_history`를 보면서도 **현재 질문의 의도를 독립적으로 판단**. 이전 토픽에 끌려가지 않음.

### InfoAgent

```
1차 호출:
  프롬프트에 대화 이력 포함:
    [이전 대화 이력]
    - Q: CVR-L1-TFT-01에 Lot 뭐 있어? → intent: lot_query

  하지만 도구 선택은 현재 의도(equipment_status)에 맞춰:
  tool_calls: [get_equipment_status({"line":"L2"})]

ToolNode 실행 (SQL):
  SELECT status, COUNT(*) FROM equipment WHERE line = 'L2' GROUP BY status
  SELECT equipment_id, equipment_type, line, zone, status FROM equipment WHERE line = 'L2'

ToolMessage:
  {"summary":[{"status":"RUNNING","cnt":4}],
   "equipment":[
     {"equipment_id":"CRN-L2-PACK-01","equipment_type":"CRANE","status":"RUNNING"},
     {"equipment_id":"CVR-L2-CELL-01","equipment_type":"CONVEYOR","status":"RUNNING"},
     {"equipment_id":"SHT-L2-TFT-01","equipment_type":"SHUTTLE","status":"RUNNING"},
     {"equipment_id":"STK-L2-TFT-01","equipment_type":"STACKER","status":"RUNNING"}
   ]}
```

### ResponseAgent

```
final_answer:
  L2 라인의 장비 상태:
  | 상태    | 대수 |
  | RUNNING | 4    |

  | 장비 ID         | 유형     | 구간   | 상태    |
  | CRN-L2-PACK-01  | CRANE    | PACK   | RUNNING |
  | CVR-L2-CELL-01  | CONVEYOR | CELL   | RUNNING |
  | SHT-L2-TFT-01   | SHUTTLE  | TFT    | RUNNING |
  | STK-L2-TFT-01   | STACKER  | TFT    | RUNNING |
```

---

## State 변화 요약 (2턴)

| 턴 | user_input | history | intent | tools |
|----|------------|---------|--------|-------|
| 1 | "CVR-L1-TFT-01에 Lot 뭐 있어?" | 0턴 | `lot_query` | `get_lots_on_equipment` + `get_lots_scheduled_for_equipment` |
| 2 | "L2 장비 상태 어때?" | 1턴 | `equipment_status` | `get_equipment_status` |

```
Turn 1: lot_query      ─── Lot 2개 Tool 동시 호출 ──→ 📍📅 Lot 구분 응답
Turn 2: equipment_status ─── 완전 다른 Tool ──────────→ 장비 상태 집계
```

---

## 학습 포인트

1. **토픽 전환 시 intent 독립 판단**: `conversation_history`에 이전 토픽(lot_query)이 있지만, IntentAgent가 현재 질문만으로 `equipment_status`를 정확히 분류. 이전 문맥에 "오염"되지 않음.
2. **이력은 참고용, 결정은 현재 질문 기준**: 프롬프트 설계에서 "이전 대화를 **참고**하되, 현재 질문의 의도를 분석하세요"라고 지시한 것이 핵심.
3. **Tool 선택도 완전 전환**: Turn 1은 Lot Tool 2개, Turn 2는 장비 Tool 1개. 이전 턴의 Tool과 무관하게 현재 의도에 맞는 Tool만 호출.
4. **messages는 턴마다 리셋**: Turn 2의 `messages: []`는 빈 상태에서 시작. Turn 1의 Tool 결과(Lot 데이터)가 Turn 2로 유출되지 않음. `conversation_history`만 요약 형태로 전달.
5. **실무 의미**: 사용자는 대화 중 자유롭게 토픽을 바꿈. 시스템이 이전 토픽에 갇히면 UX가 나빠짐. `conversation_history`는 문맥 유지용이지, 의도 강제가 아님.
