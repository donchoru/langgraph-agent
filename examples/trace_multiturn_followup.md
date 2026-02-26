# 예시 9: 멀티턴 연속 대화 — 같은 주제 심화 (overload → L1 필터 → 장비 상세)

> **학습 목표**: 3턴에 걸쳐 같은 주제를 점점 좁혀가는 멀티턴 대화 패턴.
> `conversation_history`가 IntentAgent와 InfoAgent에 어떻게 전달되어 문맥을 유지하는지 추적한다.

---

## 대화 흐름

```
Turn 1: "과부하 장비 있어?"
Turn 2: "그 중에서 L1 라인만 보여줘"     ← "그 중에서" = 이전 턴 참조
Turn 3: "CVR-L1-CELL-01 상세 정보 알려줘"  ← Turn2 결과에서 특정 장비 선택
```

---

## Turn 1: 과부하 장비 있어?

### IntentAgent

```
State BEFORE:
  user_input: "과부하 장비 있어?"
  conversation_history: 0턴    ← 첫 턴이므로 이력 없음
  intent: ""

LLM 입력: "과부하 장비 있어?"    ← 이력 없으므로 질문만 전달

LLM 출력:
  intent: "overload_check"
  detail: {"equipment_type":"","line":"","zone":"","equipment_id":"","lot_id":"","hours":0}
  reasoning: "과부하 장비 확인 요청"
```

### InfoAgent → ToolNode → InfoAgent 재진입

```
1차 호출:
  tool_calls: [get_overloaded_equipment({})]

ToolNode 실행 (SQL):
  SELECT e.equipment_id, e.equipment_type, e.line, e.zone, e.status,
         lr.load_rate_pct, at.warning_pct, at.critical_pct
  FROM load_rate lr
  JOIN equipment e ON lr.equipment_id = e.equipment_id
  JOIN alert_threshold at ON e.equipment_type = at.equipment_type
  WHERE lr.load_rate_pct >= at.warning_pct
    AND lr.recorded_at >= datetime('now', 'localtime', '-1 hours')

ToolMessage 결과 (발췌):
  [
    {"equipment_id":"CVR-L1-CELL-01", "line":"L1", "load_rate_pct":99.8, "status":"ERROR"},
    {"equipment_id":"SHT-L3-CELL-01", "line":"L3", "load_rate_pct":99.3, "status":"ERROR"},
    {"equipment_id":"AGV-L1-CELL-01", "line":"L1", "load_rate_pct":99.1, "status":"ERROR"},
    ...
  ]

2차 호출 (재진입) → 텍스트 응답 생성
```

### ResponseAgent

```
final_answer:
  🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.
  | 장비 ID         | 유형     | 라인 | 구간   | 부하율(%) | 상태  |
  | CVR-L1-CELL-01  | CONVEYOR | L1   | CELL   | 99.8      | ERROR |
  | SHT-L3-CELL-01  | SHUTTLE  | L3   | CELL   | 99.3      | ERROR |
  | AGV-L1-CELL-01  | AGV      | L1   | CELL   | 99.1      | ERROR |
  | ...
```

### Turn 1 완료 후 conversation_history에 저장

```python
conversation_history = [
    {
        "user": "과부하 장비 있어?",
        "answer": "🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다...",
        "intent": "overload_check"
    }
]
```

---

## Turn 2: 그 중에서 L1 라인만 보여줘

### IntentAgent — ⚡ 핵심: 대화 이력 참조

```
State BEFORE:
  user_input: "그 중에서 L1 라인만 보여줘"
  conversation_history: 1턴
    - Q: "과부하 장비 있어?" → overload_check

LLM 입력 (conversation_history 포함):
  [이전 대화 이력]
  사용자: 과부하 장비 있어?
  의도: overload_check
  응답 요약: 🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다...

  [현재 질문]
  그 중에서 L1 라인만 보여줘

  위 대화 이력을 참고하여 현재 질문의 의도를 분석하세요.
  '그럼', '거기', '그 설비' 등 대명사는 이전 대화에서 언급된 대상을 참조합니다.

LLM 출력:
  intent: "overload_check"           ← 이전 턴과 같은 의도
  detail: {"line":"L1", ...}         ← "그 중에서 L1" → line 필터 추출
  reasoning: "이전 대화에서 과부하 장비를 조회했고, L1 라인만 필터링 요청"
```

**포인트**: "그 중에서"라는 대명사를 `conversation_history`의 이전 턴(overload_check)을 참조하여 해석.
코드 로직이 아니라 **LLM이 문맥을 읽고 판단**.

### InfoAgent

```
1차 호출:
  프롬프트에 대화 이력 주입:
    [이전 대화 이력]
    - Q: 과부하 장비 있어? → intent: overload_check, 응답: 🚨 최근 1시간...

  tool_calls: [get_overloaded_equipment({})]  ← 필터는 LLM이 응답 시 적용

ToolNode → 전체 과부하 장비 데이터 반환

2차 호출 (재진입):
  LLM이 Tool 결과에서 L1 라인만 필터링하여 응답 생성
```

### ResponseAgent

```
final_answer:
  🚨 L1 라인 과부하 장비 목록:
  | 장비 ID         | 유형     | 구간 | 부하율(%) |
  | CVR-L1-CELL-01  | CONVEYOR | CELL | 99.8      |
  | AGV-L1-CELL-01  | AGV      | CELL | 99.1      |
```

---

## Turn 3: CVR-L1-CELL-01 상세 정보 알려줘

### IntentAgent

```
conversation_history: 2턴
  - Q: "과부하 장비 있어?" → overload_check
  - Q: "그 중에서 L1 라인만 보여줘" → overload_check

LLM 출력:
  intent: "equipment_status"         ← 의도 변경! (과부하 → 장비 상세)
  detail: {"equipment_id":"CVR-L1-CELL-01"}
```

**포인트**: 같은 주제(과부하 장비) 안에서 의도가 자연스럽게 전환.

### InfoAgent → ToolNode

```
tool_calls: [get_equipment_detail({"equipment_id":"CVR-L1-CELL-01"})]

SQL:
  SELECT * FROM equipment WHERE equipment_id = 'CVR-L1-CELL-01'
  SELECT ... FROM load_rate WHERE equipment_id = 'CVR-L1-CELL-01' LIMIT 24
  SELECT ... FROM alert_history WHERE equipment_id = 'CVR-L1-CELL-01' LIMIT 10

결과: 장비 기본 정보 + 부하율 이력 24건 + 알림 이력 10건
```

### ResponseAgent

```
final_answer:
  CVR-L1-CELL-01 상세 정보:
  - 유형: CONVEYOR, L1-CELL, 상태: ERROR
  - 최근 부하율: 91~99% (지속 과부하)
  - 알림 이력: CRITICAL 7건, WARNING 3건
```

---

## State 변화 요약 (3턴)

| 턴 | user_input | history | intent | tools |
|----|------------|---------|--------|-------|
| 1 | "과부하 장비 있어?" | 0턴 | `overload_check` | `get_overloaded_equipment` |
| 2 | "그 중에서 L1 라인만 보여줘" | 1턴 | `overload_check` | `get_overloaded_equipment` |
| 3 | "CVR-L1-CELL-01 상세 정보 알려줘" | 2턴 | `equipment_status` | `get_equipment_detail` |

---

## 학습 포인트

1. **conversation_history 전달 구조**: main.py가 매 턴 후 `{user, answer, intent}`를 누적 → 다음 턴의 `AgentState`에 주입 → IntentAgent/InfoAgent의 LLM 프롬프트에 포함.
2. **대명사 해소는 LLM이 수행**: "그 중에서"를 코드로 파싱하지 않음. LLM이 `conversation_history`를 읽고 이전 턴의 과부하 장비 목록을 참조.
3. **messages는 매턴 초기화**: `messages: []`로 시작 → Tool 루프는 턴 내에서만 발생. 턴 간 문맥은 `conversation_history`가 담당. 이 분리가 핵심.
4. **같은 주제 내 의도 전환**: Turn 1,2는 `overload_check`, Turn 3은 `equipment_status`. 대화 주제가 같아도 의도는 자유롭게 바뀔 수 있음.
5. **필터링은 LLM이 응답 단계에서 처리**: Turn 2에서 `get_overloaded_equipment`는 전체 데이터를 반환하지만, LLM이 재진입 시 L1만 필터링하여 응답 생성. Tool 파라미터로 필터하는 것과 LLM이 결과를 필터하는 것은 다른 전략.
