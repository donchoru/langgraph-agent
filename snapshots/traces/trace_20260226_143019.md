# Agent Trace Log
- **시간**: 2026-02-26 14:30:19
- **사용자 입력**: L2 구간별 부하율 요약해줘
- **최종 의도**: load_rate_query

---
## Step 1: IntentAgent (의도분석)
### INPUT
```
L2 구간별 부하율 요약해줘
```
### OUTPUT
- intent: `load_rate_query`
- detail: `{"equipment_type": "", "line": "L2", "zone": "", "equipment_id": "", "hours": 0, "keyword": "요약"}`
- reasoning: L2 구간별 부하율을 요약해달라는 요청은 특정 라인의 부하율 수치 조회를 의미합니다.

---
## Step 2: InfoAgent (정보조회)
### INPUT
- intent: `load_rate_query`
- detail: `{"equipment_type": "", "line": "L2", "zone": "", "equipment_id": "", "hours": 0, "keyword": "요약"}`
### TOOL CALLS
- `get_zone_summary({'line': 'L2'})`

---
## Step 2: InfoAgent (정보조회)
### INPUT
- intent: `load_rate_query`
- detail: `{"equipment_type": "", "line": "L2", "zone": "", "equipment_id": "", "hours": 0, "keyword": "요약"}`

---
## Step 3: ResponseAgent (응답생성)
### OUTPUT
```

L2 라인의 구간별 부하율 요약입니다.

| 구간   | 평균 부하율 | 최대 부하율 | 최소 부하율 | 장비 수 |
| :----- | :---------- | :---------- | :---------- | :------ |
| CELL   | 46.5        | 64.0        | 25.8        | 1       |
| MODULE | 63.7        | 84.8        | 27.7        | 1       |
| PACK   | 57.4        | 70.3        | 44.5        | 1       |
| TFT    | 43.9        | 53.2        | 28.1        | 1       |
```