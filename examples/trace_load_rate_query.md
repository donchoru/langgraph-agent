# Agent Trace Log
- **시간**: 2026-02-26 14:30:14
- **사용자 입력**: L1 컨베이어 부하율 알려줘
- **최종 의도**: load_rate_query

---
## Step 1: IntentAgent (의도분석)
### INPUT
```
L1 컨베이어 부하율 알려줘
```
### OUTPUT
- intent: `load_rate_query`
- detail: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- reasoning: L1 컨베이어의 부하율을 묻는 질문이므로 load_rate_query 의도에 해당함

---
## Step 2: InfoAgent (정보조회)
### INPUT
- intent: `load_rate_query`
- detail: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
### TOOL CALLS
- `get_load_rates({'line': 'L1', 'equipment_type': 'CONVEYOR'})`

---
## Step 2: InfoAgent (정보조회)
### INPUT
- intent: `load_rate_query`
- detail: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`

---
## Step 3: ResponseAgent (응답생성)
### OUTPUT
```
1시간 동안 L1 라인의 컨베이어 부하율입니다.

| 장비 ID        | 부하율(%) | 상태    |
| ------------- | ------- | ----- |
| CVR-L1-CELL-01 | 98.3    | ERROR |
| CVR-L1-PACK-01 | 70.6    | RUNNING |
| CVR-L1-TFT-01  | 40.7    | RUNNING |
| CVR-L1-TFT-02  | 29.9    | RUNNING |
```