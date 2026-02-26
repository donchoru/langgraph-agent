# 예시 3: 구간별 부하율 요약 (load_rate_query → get_zone_summary)

> **학습 목표**: 같은 `load_rate_query` 의도라도 "요약" 키워드에 따라 **다른 Tool**이 선택되는 과정을 추적한다. LLM의 Tool 선택 능력을 보여주는 예시.

---

## 사용자 입력

```
L2 구간별 부하율 요약해줘
```

## 에이전트 처리 흐름

```
사용자: "L2 구간별 부하율 요약해줘"
  │
  ▼
[Step 1] IntentAgent
  │  intent: "load_rate_query"     ← 예시 2와 같은 의도!
  │  detail: {"line":"L2", "keyword":"요약"}
  │  ← "요약" 키워드를 별도 추출
  │
  ▼
[Step 2] InfoAgent (1차)
  │  LLM 판단: "요약" + "구간별" → get_load_rates가 아니라 get_zone_summary!
  │  tool_calls: [get_zone_summary({"line":"L2"})]
  │
  ▼
[Step 2.5] ToolNode
  │  SQL: GROUP BY e.line, e.zone → 구간별 AVG/MAX/MIN 집계
  │
  ▼
[Step 2 재진입] InfoAgent (2차) → 집계 결과 표로 정리
  │
  ▼
[Step 3] ResponseAgent → final_answer 설정
```

---

## 핵심 설계 포인트

### 1. 같은 intent, 다른 Tool — LLM의 판단력

예시 2 (`"L1 컨베이어 부하율 알려줘"`)와 이 예시는 둘 다 `load_rate_query` 의도이지만:

| 질문 | intent | keyword | 선택된 Tool |
|------|--------|---------|------------|
| L1 컨베이어 부하율 알려줘 | `load_rate_query` | `""` | `get_load_rates` (개별 데이터) |
| **L2 구간별 부하율 요약해줘** | **`load_rate_query`** | **`"요약"`** | **`get_zone_summary`** (집계 데이터) |

`INFO_SYSTEM_PROMPT`의 도구 선택 가이드:
```
load_rate_query 의도 → get_load_rates (+ 필요시 get_zone_summary)
```

"필요시"를 LLM이 스스로 판단: "요약" + "구간별" 키워드를 보고 `get_zone_summary` 선택.

### 2. 집계 SQL vs 개별 SQL

**get_load_rates** (예시 2):
```sql
SELECT e.equipment_id, ..., lr.load_rate_pct, lr.throughput, lr.queue_length
FROM load_rate lr JOIN equipment e ...
-- → 개별 장비별 row 반환
```

**get_zone_summary** (이 예시):
```sql
SELECT e.line, e.zone,
       COUNT(DISTINCT e.equipment_id) as equipment_count,
       ROUND(AVG(lr.load_rate_pct), 1) as avg_load,
       ROUND(MAX(lr.load_rate_pct), 1) as max_load,
       ROUND(MIN(lr.load_rate_pct), 1) as min_load
FROM load_rate lr JOIN equipment e ...
WHERE lr.recorded_at >= datetime('now', 'localtime', '-1 hours')
  AND e.line = 'L2'
GROUP BY e.line, e.zone
ORDER BY e.line, e.zone
```

**핵심 차이**: `GROUP BY`로 구간별 집계. 장비 수십 대의 데이터를 4개 구간으로 압축.

### 3. IntentAgent의 keyword 필드

```json
{
  "intent": "load_rate_query",
  "detail": {
    "equipment_type": "",
    "line": "L2",
    "zone": "",
    "equipment_id": "",
    "hours": 0,
    "keyword": "요약"     // ← 이 필드가 핵심
  },
  "reasoning": "L2 구간별 부하율을 요약해달라는 요청은 특정 라인의 부하율 수치 조회를 의미합니다."
}
```

`keyword`는 intent 분류 외의 추가 정보. InfoAgent LLM이 이 값을 보고 Tool 선택에 반영.

---

## Tool 결과 데이터

```json
[
  {"line": "L2", "zone": "CELL", "equipment_count": 2, "avg_load": 52.3, "max_load": 68.7, "min_load": 35.9},
  {"line": "L2", "zone": "MODULE", "equipment_count": 3, "avg_load": 61.8, "max_load": 84.8, "min_load": 38.2},
  {"line": "L2", "zone": "PACK", "equipment_count": 2, "avg_load": 45.1, "max_load": 57.3, "min_load": 32.9},
  {"line": "L2", "zone": "TFT", "equipment_count": 2, "avg_load": 48.6, "max_load": 62.4, "min_load": 34.8}
]
```

**데이터 해석**:
- MODULE 구간: `max_load: 84.8` — CRANE의 경고 기준(70%)을 초과하는 장비 존재
- CELL/PACK/TFT: 평균 45~52% — 전반적으로 여유

## 최종 응답 (final_answer)

```
L2 라인의 구간별 부하율 요약입니다 (최근 1시간).

| 구간   | 장비 수 | 평균(%) | 최대(%) | 최소(%) |
| :----- | :------ | :------ | :------ | :------ |
| CELL   | 2       | 52.3    | 68.7    | 35.9    |
| MODULE | 3       | 61.8    | 84.8    | 38.2    |
| PACK   | 2       | 45.1    | 57.3    | 32.9    |
| TFT    | 2       | 48.6    | 62.4    | 34.8    |
```

---

## 예시 2 vs 예시 3 비교

| 항목 | 예시 2 (부하율 조회) | 예시 3 (구간별 요약) |
|------|---------------------|---------------------|
| 질문 | L1 컨베이어 부하율 알려줘 | L2 구간별 부하율 요약해줘 |
| intent | `load_rate_query` | `load_rate_query` |
| Tool | `get_load_rates` | `get_zone_summary` |
| SQL | `SELECT ... ORDER BY` | `SELECT ... GROUP BY ... AVG/MAX/MIN` |
| 결과 | 개별 장비 데이터 4건 | 구간별 집계 4건 |
| 응답 | 장비별 부하율 테이블 | 구간별 평균/최대/최소 테이블 |

---

## 학습 포인트

1. **같은 intent, 다른 Tool**: 의도 분류는 5가지로 단순하지만, Tool은 7개. LLM이 `keyword`, `zone` 등 추가 정보로 적절한 Tool을 선택. 이것이 LLM 기반 Tool 선택의 유연성.
2. **집계 vs 상세**: `get_zone_summary`는 `GROUP BY`로 데이터를 압축. 사용자가 "요약"을 원하는지 "상세"를 원하는지에 따라 적합한 granularity의 데이터를 반환.
3. **Tool 설계 원칙**: 비슷한 데이터를 다루더라도 목적이 다르면 별도 Tool로 분리 (`get_load_rates` vs `get_zone_summary`). LLM이 선택하기 쉽도록 각 Tool의 docstring을 명확히 작성.
