# 예시 6: 과부하 원인 연쇄 분석 (멀티 Tool 동시 호출)

> **학습 목표**: 복잡한 질문에 LLM이 **3개 Tool을 한 번에 병렬 호출**하여 다각도 데이터를 수집하고, 종합 분석 응답을 생성하는 과정을 추적한다. 단일 Tool 호출(예시 1~4)과의 핵심 차이를 이해한다.

---

## 사용자 입력

```
CVR-L1-CELL-01이 과부하인데, 왜 그런지 원인 분석해줘. 같은 라인 다른 장비 상태랑 최근 알림도 같이 봐줘.
```

**질문의 복잡도**: 3가지 요구사항이 하나의 질문에 포함됨
1. "CVR-L1-CELL-01 왜 과부하야?" → 장비 상세 + 이력 필요
2. "같은 라인 다른 장비 상태" → L1 전체 장비 상태 필요
3. "최근 알림도 같이 봐줘" → 알림 이력 필요

---

## 에이전트 처리 흐름

```
사용자: "CVR-L1-CELL-01이 과부하인데, 왜 그런지 원인 분석해줘..."
  │
  ▼
[Step 1] IntentAgent
  │  intent: "overload_check"
  │  detail: {"equipment_type":"CONVEYOR", "line":"L1", "zone":"CELL",
  │           "equipment_id":"CVR-L1-CELL-01", "keyword":"원인 분석"}
  │
  ▼
[Step 2] InfoAgent (1차) ── ★ 3개 Tool 동시 호출 ★
  │  LLM이 질문의 3가지 요구사항을 각각 다른 Tool로 매핑:
  │  tool_calls: [
  │    get_equipment_detail({"equipment_id": "CVR-L1-CELL-01"}),  ← 요구 ①
  │    get_equipment_status({"line": "L1"}),                      ← 요구 ②
  │    get_recent_alerts({"hours": 24})                           ← 요구 ③
  │  ]
  │
  ▼
[Step 2.5] ToolNode ── 3개 SQL 병렬 실행
  │  ToolMessage × 3 반환:
  │  [1] 장비 상세 + 부하율 24건 + 알림 10건
  │  [2] L1 장비 14대 상태 (ERROR 5, RUNNING 6, MAINTENANCE 2, IDLE 1)
  │  [3] 전체 알림 ~250건
  │
  ▼
[Step 2 재진입] InfoAgent (2차) ── 3개 Tool 결과 종합
  │  messages: [AIMessage(tool_calls×3), ToolMessage×3] = 4건
  │  LLM이 3개 결과를 하나의 분석 응답으로 종합
  │
  ▼
[Step 3] ResponseAgent → final_answer 설정
```

### 예시 1(단일 Tool)과의 차이

```
[예시 1: 단일 Tool]
InfoAgent → get_overloaded_equipment() → ToolNode → InfoAgent → 응답
           ↑ Tool 1개                    ↑ ToolMessage 1개

[예시 6: 멀티 Tool]
InfoAgent → get_equipment_detail()  ┐
            get_equipment_status()  ├→ ToolNode → InfoAgent → 응답
            get_recent_alerts()     ┘
           ↑ Tool 3개 동시             ↑ ToolMessage 3개
```

---

## 핵심 설계 포인트

### 1. IntentAgent의 복합 질문 해석

```json
{
  "intent": "overload_check",
  "detail": {
    "equipment_type": "CONVEYOR",
    "line": "L1",
    "zone": "CELL",
    "equipment_id": "CVR-L1-CELL-01",
    "hours": 0,
    "keyword": "원인 분석"
  },
  "reasoning": "특정 장비의 과부하 원인 분석 요청이므로 overload_check 의도에 해당함. 같은 라인 다른 장비 상태 및 알림 확인 요청은 overload_check에 포함되는 내용으로 판단."
}
```

**포인트**: 질문에 3가지 요구가 있지만 intent는 하나(`overload_check`). 세부 요구사항의 분해는 IntentAgent가 아니라 **InfoAgent LLM**이 Tool 선택 시점에 처리한다.

### 2. LLM의 멀티 Tool 동시 호출 결정

InfoAgent의 1차 LLM 호출에서 Gemini가 반환한 `tool_calls`:

```python
[
    {"name": "get_equipment_detail", "args": {"equipment_id": "CVR-L1-CELL-01"}},
    {"name": "get_equipment_status", "args": {"line": "L1"}},
    {"name": "get_recent_alerts", "args": {"hours": 24}},
]
```

**왜 3개를 동시에?**
- Gemini Function Calling은 **parallel tool calls**를 지원
- LLM이 질문을 분석하여 "3가지 데이터가 모두 필요하다"고 판단
- 순차 호출(3번 루프)보다 **1번의 ToolNode 실행으로 3개 결과를 한꺼번에** 받음
- 응답 시간: 순차 ~9초 vs 병렬 ~3초

### 3. 실행된 SQL 3개

**Tool 1: get_equipment_detail("CVR-L1-CELL-01")**
```sql
-- 장비 기본 정보
SELECT * FROM equipment WHERE equipment_id = 'CVR-L1-CELL-01'

-- 부하율 이력 (최근 24건 = 4시간)
SELECT recorded_at, load_rate_pct, throughput, queue_length
FROM load_rate WHERE equipment_id = 'CVR-L1-CELL-01'
ORDER BY recorded_at DESC LIMIT 24

-- 알림 이력 (최근 10건)
SELECT alert_type, load_rate_pct, threshold_pct, triggered_at, message
FROM alert_history WHERE equipment_id = 'CVR-L1-CELL-01'
ORDER BY triggered_at DESC LIMIT 10
```

**Tool 2: get_equipment_status(line="L1")**
```sql
-- 상태별 집계
SELECT status, COUNT(*) as cnt FROM equipment
WHERE line = 'L1' GROUP BY status ORDER BY cnt DESC

-- 장비 목록
SELECT equipment_id, equipment_type, line, zone, status FROM equipment
WHERE line = 'L1' ORDER BY status, equipment_id
```

**Tool 3: get_recent_alerts(hours=24)**
```sql
SELECT ah.*, e.equipment_type, e.line, e.zone
FROM alert_history ah
JOIN equipment e ON ah.equipment_id = e.equipment_id
WHERE triggered_at >= datetime('now', 'localtime', '-24 hours')
ORDER BY triggered_at DESC
```

**총 6개 SQL 쿼리**가 3개 Tool 안에서 실행됨.

### 4. LLM의 3개 결과 종합 과정

InfoAgent 2차 호출 시 LLM에 전달되는 messages:
```
[0] AIMessage(tool_calls=[3개 Tool 호출])
[1] ToolMessage(tool=get_equipment_detail, content={장비상세JSON})
[2] ToolMessage(tool=get_equipment_status, content={L1상태JSON})
[3] ToolMessage(tool=get_recent_alerts, content={알림250건JSON})
```

LLM이 이 4개 메시지를 보고 생성하는 응답의 구조:
1. **CVR-L1-CELL-01 상세** — Tool 1 결과에서 추출
2. **L1 라인 전체 상태** — Tool 2 결과에서 추출
3. **알림 이력** — Tool 3 결과에서 추출 + "L1 라인에 에러 장비가 많으니 확인 필요" 종합 판단

---

## Tool 1 결과: 장비 상세

```json
{
  "equipment": [{
    "equipment_id": "CVR-L1-CELL-01",
    "equipment_type": "CONVEYOR",
    "line": "L1",
    "zone": "CELL",
    "status": "ERROR",
    "installed_date": "2024-11-21",
    "description": "CONVEYOR L1-CELL"
  }],
  "load_history": [
    {"recorded_at": "2026-02-26 18:06:00", "load_rate_pct": 98.3, "throughput": 84, "queue_length": 17},
    {"recorded_at": "2026-02-26 17:56:00", "load_rate_pct": 96.9, "throughput": 97, "queue_length": 2},
    {"recorded_at": "2026-02-26 17:46:00", "load_rate_pct": 84.6, "throughput": 69, "queue_length": 0},
    {"recorded_at": "2026-02-26 17:36:00", "load_rate_pct": 86.3, "throughput": 81, "queue_length": 7},
    {"recorded_at": "2026-02-26 17:26:00", "load_rate_pct": 99.8, "throughput": 119, "queue_length": 15}
  ],
  "recent_alerts": [
    {"alert_type": "CRITICAL", "load_rate_pct": 98.3, "threshold_pct": 95.0, "triggered_at": "2026-02-26 18:06:00"},
    {"alert_type": "CRITICAL", "load_rate_pct": 96.9, "threshold_pct": 95.0, "triggered_at": "2026-02-26 17:56:00"},
    {"alert_type": "WARNING", "load_rate_pct": 84.6, "threshold_pct": 80.0, "triggered_at": "2026-02-26 17:46:00"},
    {"alert_type": "CRITICAL", "load_rate_pct": 99.8, "threshold_pct": 95.0, "triggered_at": "2026-02-26 17:26:00"},
    {"alert_type": "CRITICAL", "load_rate_pct": 97.2, "threshold_pct": 95.0, "triggered_at": "2026-02-26 17:06:00"}
  ]
}
```

**데이터 해석 — 과부하 패턴 발견**:
- 부하율이 84~99%를 오가며 **지속적으로 높은 상태** (간헐적이 아님)
- `queue_length: 17` → 대기열 적체 심각 (처리 속도 < 유입 속도)
- CRITICAL 알림이 4시간 중 4회 → 만성적 과부하

## Tool 2 결과: L1 라인 전체 상태

```json
{
  "summary": [
    {"status": "RUNNING", "cnt": 6},
    {"status": "ERROR", "cnt": 5},
    {"status": "MAINTENANCE", "cnt": 2},
    {"status": "IDLE", "cnt": 1}
  ],
  "equipment": [
    {"equipment_id": "AGV-L1-CELL-01", "equipment_type": "AGV", "status": "ERROR"},
    {"equipment_id": "CRN-L1-MODULE-01", "equipment_type": "CRANE", "status": "ERROR"},
    {"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "status": "ERROR"},
    {"equipment_id": "SHT-L1-TFT-01", "equipment_type": "SHUTTLE", "status": "ERROR"},
    {"equipment_id": "SHT-L1-TFT-02", "equipment_type": "SHUTTLE", "status": "ERROR"},
    {"equipment_id": "STK-L1-PACK-02", "equipment_type": "STACKER", "status": "IDLE"},
    {"equipment_id": "CRN-L1-CELL-02", "equipment_type": "CRANE", "status": "MAINTENANCE"},
    {"equipment_id": "SHT-L1-CELL-01", "equipment_type": "SHUTTLE", "status": "MAINTENANCE"}
  ]
}
```

**데이터 해석 — 연쇄 장애 패턴 발견**:
- L1 라인 14대 중 **5대가 ERROR** (36%) — 심각한 라인 수준 문제
- CELL 구간 집중: CVR-L1-CELL-01(ERROR) + AGV-L1-CELL-01(ERROR) + CRN-L1-CELL-02(MAINTENANCE) + SHT-L1-CELL-01(MAINTENANCE)
- **CELL 구간 4대 중 2대 ERROR, 2대 MAINTENANCE** → 구간 전체가 비정상
- TFT 구간: SHT-L1-TFT-01/02 둘 다 ERROR → 상류 구간도 문제

## Tool 3 결과: 알림 이력 (최근 24시간, 상위 발췌)

```json
[
  {"equipment_id": "CVR-L1-CELL-01", "alert_type": "CRITICAL", "load_rate_pct": 98.3, "triggered_at": "2026-02-26 18:06:00"},
  {"equipment_id": "SHT-L3-CELL-01", "alert_type": "CRITICAL", "load_rate_pct": 98.1, "triggered_at": "2026-02-26 18:06:00"},
  {"equipment_id": "AGV-L1-CELL-01", "alert_type": "CRITICAL", "load_rate_pct": 94.7, "triggered_at": "2026-02-26 18:06:00"},
  {"equipment_id": "CRN-L1-MODULE-01", "alert_type": "CRITICAL", "load_rate_pct": 88.8, "triggered_at": "2026-02-26 18:06:00"},
  {"equipment_id": "SHT-L1-TFT-02", "alert_type": "WARNING", "load_rate_pct": 88.8, "triggered_at": "2026-02-26 18:06:00"}
]
```

**데이터 해석**: 같은 시각 L1 라인에서 CRITICAL 3건 동시 발생 → **라인 수준의 연쇄 과부하**.

---

## 최종 응답 (final_answer)

```
1. CVR-L1-CELL-01 장비 상세 정보입니다.

|  항목           |  내용               |
|----------------|---------------------|
| 장비 ID         | CVR-L1-CELL-01      |
| 유형            | CONVEYOR            |
| 라인            | L1                  |
| 구간            | CELL                |
| 상태            | ERROR               |
| 최근 부하율      | 98.3% (CRITICAL)    |

지난 24시간 CVR-L1-CELL-01 알림 이력:
| 발생 시각            | 알림 유형  | 부하율  |
|---------------------|----------|--------|
| 2026-02-26 18:06    | CRITICAL | 98.3%  |
| 2026-02-26 17:56    | CRITICAL | 96.9%  |
| 2026-02-26 17:26    | CRITICAL | 99.8%  |
| 2026-02-26 17:06    | CRITICAL | 97.2%  |
| ...                 |          |        |

2. L1 라인 장비 상태 요약입니다.

| 상태          | 장비 수 |
|--------------|--------|
| RUNNING      | 6      |
| ERROR        | 5      |
| MAINTENANCE  | 2      |
| IDLE         | 1      |

3. 24시간 알림 이력에서 L1 라인 CRITICAL 알림이 집중 발생.
   현재 L1 라인에 에러가 발생한 장비가 많으니 확인이 필요합니다.
```

---

## State 변화 요약

| 단계 | messages 수 | 핵심 변화 |
|------|------------|----------|
| 초기 | 0 | — |
| IntentAgent 후 | 0 | intent=`overload_check`, equipment_id 추출 |
| InfoAgent 1차 | 1 | **AIMessage에 tool_calls 3개** (병렬) |
| ToolNode 후 | 4 | **ToolMessage 3개** 추가 (장비상세+L1상태+알림) |
| InfoAgent 2차 | 5 | 3개 결과 종합 → 텍스트 응답 |
| ResponseAgent | 5 | final_answer 설정 |

### 예시 1(단일 Tool)과 비교

| 항목 | 예시 1 (단일) | 예시 6 (멀티) |
|------|-------------|-------------|
| 질문 복잡도 | 단일 요구 | 3가지 요구 복합 |
| Tool 호출 수 | 1개 | **3개 동시** |
| SQL 실행 수 | 1~2개 | **6개** |
| messages 최종 | 3개 | **5개** |
| ToolNode 진입 | 1회 | **1회** (병렬이므로) |
| Tool 루프 | 1회 | **1회** (동시 호출이므로 루프 불필요) |

---

## 학습 포인트

1. **Parallel Tool Calls**: Gemini Function Calling이 여러 Tool을 한 번에 호출할 수 있다. LangGraph의 ToolNode는 `tool_calls` 배열의 모든 Tool을 실행하고 각각의 ToolMessage를 반환. 순차 루프(3회)보다 병렬 호출(1회)이 응답 시간을 크게 줄인다.

2. **질문 분해는 InfoAgent가 한다**: IntentAgent는 intent 하나만 분류. "3가지 데이터가 필요하다"는 판단은 InfoAgent의 LLM이 Tool 선택 시점에 수행. 이것이 LLM 기반 에이전트의 유연성 — 규칙으로 분해하지 않아도 LLM이 자연어를 분석하여 필요한 데이터를 판단.

3. **데이터 종합 능력**: LLM이 3개 Tool의 결과(장비 상세 + L1 전체 상태 + 알림 이력)를 하나의 응답으로 조합. 단순 나열이 아니라 "L1 라인에 에러 장비가 많으니 확인이 필요합니다"라는 **종합 판단**까지 추가.

4. **연쇄 분석의 한계와 확장**: 현재 시스템은 "왜 과부하인지"에 대해 데이터를 보여주지만, `production-anomaly` 프로젝트처럼 상류 설비 추적, 정비 이력 연쇄 분석까지는 하지 않음. 확장하려면 `get_upstream_equipment()` 같은 Tool을 추가하고, INFO_SYSTEM_PROMPT에 "원인 분석 시 상류 설비도 확인하라"는 가이드를 넣으면 된다.
