# 예시 2: 부하율 조회 (load_rate_query)

> **학습 목표**: IntentAgent가 사용자 질문에서 **구체적인 파라미터**(장비유형, 라인)를 추출하고, InfoAgent가 이를 Tool 호출 인자로 전달하는 과정을 추적한다.

---

## 사용자 입력

```
L1 컨베이어 부하율 알려줘
```

## 에이전트 처리 흐름

```
사용자: "L1 컨베이어 부하율 알려줘"
  │
  ▼
[Step 1] IntentAgent
  │  intent: "load_rate_query"
  │  detail: {"equipment_type":"CONVEYOR", "line":"L1", ...}
  │  ← "컨베이어" → CONVEYOR, "L1" → L1 매핑 수행
  │
  ▼
[Step 2] InfoAgent (1차)
  │  LLM이 intent_detail을 참고하여 Tool 파라미터 결정
  │  tool_calls: [get_load_rates({"equipment_type":"CONVEYOR", "line":"L1"})]
  │
  ▼
[Step 2.5] ToolNode
  │  SQL 실행 → L1 라인 CONVEYOR 4대의 최근 1시간 부하율 반환
  │
  ▼
[Step 2 재진입] InfoAgent (2차)
  │  Tool 결과 JSON → 마크다운 표로 정리
  │
  ▼
[Step 3] ResponseAgent → final_answer 설정
```

---

## 핵심 설계 포인트

### 1. IntentAgent의 한국어 → 영문 매핑

```json
{
  "intent": "load_rate_query",
  "detail": {
    "equipment_type": "CONVEYOR",   // "컨베이어" → CONVEYOR
    "line": "L1",                    // "L1" 그대로
    "zone": "",                      // 미지정
    "equipment_id": "",
    "hours": 0,                      // 기본값 (Tool에서 1시간 적용)
    "keyword": ""
  },
  "reasoning": "L1 컨베이어의 부하율을 묻는 질문이므로 load_rate_query 의도에 해당함"
}
```

**포인트**: `INTENT_SYSTEM_PROMPT`에 매핑 테이블이 명시되어 있음:
```
컨베이어 → CONVEYOR
AGV, 무인운반차 → AGV
크레인 → CRANE
```
LLM이 이 매핑을 참고하여 한국어를 DB 컬럼값으로 변환.

### 2. InfoAgent가 detail을 Tool 파라미터로 전달하는 방식

InfoAgent는 다음 정보를 LLM에 전달:
```
의도: load_rate_query
상세: {"equipment_type":"CONVEYOR","line":"L1",...}
질문: L1 컨베이어 부하율 알려줘
```

LLM이 `detail`의 `equipment_type`과 `line`을 보고 Tool 호출 인자를 결정:
```python
get_load_rates(equipment_type="CONVEYOR", line="L1")
```

**중요**: IntentAgent가 파라미터를 추출하고, InfoAgent LLM이 이를 Tool 인자에 매핑하는 **2단계 처리**.
직접 매핑이 아니라 LLM이 판단하므로, 모호한 경우에도 유연하게 대응 가능.

### 3. 실행된 SQL (get_load_rates 내부)

```sql
SELECT e.equipment_id, e.equipment_type, e.line, e.zone, e.status,
       lr.recorded_at, lr.load_rate_pct, lr.throughput, lr.queue_length
FROM load_rate lr
JOIN equipment e ON lr.equipment_id = e.equipment_id
WHERE lr.recorded_at >= datetime('now', 'localtime', '-1 hours')
  AND e.equipment_type = 'CONVEYOR'
  AND e.line = 'L1'
ORDER BY lr.recorded_at DESC, e.equipment_id
```

**동적 WHERE 절**: `get_load_rates()`는 `equipment_type`, `line`, `zone`, `hours` 4개 파라미터를 선택적으로 받아 WHERE 조건을 동적 생성.
전달된 파라미터만 조건에 추가되므로, 같은 Tool로 다양한 조합의 조회가 가능.

### 4. 파라미터 필터링의 차이 — "전체 조회" vs "필터 조회"

| 질문 | equipment_type | line | 결과 |
|------|---------------|------|------|
| "부하율 보여줘" | `""` | `""` | 전체 30대 장비의 부하율 |
| "L1 부하율" | `""` | `"L1"` | L1 라인 전체 장비 |
| "컨베이어 부하율" | `"CONVEYOR"` | `""` | 전 라인 컨베이어 |
| **"L1 컨베이어 부하율"** | **`"CONVEYOR"`** | **`"L1"`** | **L1 컨베이어만 (4대)** |

---

## Tool 결과 데이터

```json
[
  {"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "status": "ERROR", "recorded_at": "2026-02-26 14:57:01", "load_rate_pct": 98.3, "throughput": 84, "queue_length": 17},
  {"equipment_id": "CVR-L1-PACK-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "PACK", "status": "RUNNING", "recorded_at": "2026-02-26 14:57:01", "load_rate_pct": 70.6, "throughput": 73, "queue_length": 5},
  {"equipment_id": "CVR-L1-TFT-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT", "status": "RUNNING", "recorded_at": "2026-02-26 14:57:01", "load_rate_pct": 40.7, "throughput": 45, "queue_length": 0},
  {"equipment_id": "CVR-L1-TFT-02", "equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT", "status": "RUNNING", "recorded_at": "2026-02-26 14:57:01", "load_rate_pct": 29.9, "throughput": 25, "queue_length": 0}
]
```

**데이터 해석**:
- CVR-L1-CELL-01: 98.3% — ERROR 상태, 임계값(95%) 초과. `queue_length: 17`로 대기열 적체.
- CVR-L1-PACK-01: 70.6% — 경고 수준 미만, 정상 가동.
- CVR-L1-TFT-01/02: 40.7%, 29.9% — 여유 있는 상태.

## 최종 응답 (final_answer)

```
1시간 동안 L1 라인 컨베이어의 부하율입니다.

| 장비 ID         | 부하율(%) | 상태    |
| :-------------- | :-------- | :------ |
| CVR-L1-CELL-01  | 98.3      | ERROR   |
| CVR-L1-PACK-01  | 70.6      | RUNNING |
| CVR-L1-TFT-01   | 40.7      | RUNNING |
| CVR-L1-TFT-02   | 29.9      | RUNNING |
```

---

## State 변화 요약

| 단계 | intent | messages 수 | 핵심 변화 |
|------|--------|------------|----------|
| 초기 | `""` | 0 | — |
| IntentAgent 후 | `"load_rate_query"` | 0 | intent_detail에 CONVEYOR, L1 추출 |
| InfoAgent 1차 | `"load_rate_query"` | 1 | `get_load_rates(CONVEYOR, L1)` 호출 결정 |
| ToolNode 후 | `"load_rate_query"` | 2 | SQL 결과 4건 반환 |
| InfoAgent 2차 | `"load_rate_query"` | 3 | 마크다운 표 생성 |
| ResponseAgent | `"load_rate_query"` | 3 | final_answer 설정 |

---

## 학습 포인트

1. **파라미터 추출 → 전파 체인**: 사용자의 자연어 → IntentAgent(`detail`) → InfoAgent(LLM 판단) → Tool 함수 인자. 3단계를 거치며 자연어가 SQL WHERE 조건으로 변환됨.
2. **동적 WHERE 절**: Tool 함수가 Optional 파라미터로 설계되어 있어, 같은 `get_load_rates`로 "전체 조회"부터 "L1 컨베이어만"까지 모두 처리 가능.
3. **LLM이 데이터를 요약하는 방식**: Tool 결과에는 `throughput`, `queue_length` 등 상세 데이터가 있지만, LLM은 사용자 질문("부하율 알려줘")에 맞게 `load_rate_pct`와 `status`만 추출하여 응답.
