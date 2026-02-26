# Agent Trace Log
- **시간**: 2026-02-26 14:30:08
- **사용자 입력**: 과부하 장비 있어?
- **최종 의도**: overload_check

---
## Step 1: IntentAgent (의도분석)
### INPUT
```
과부하 장비 있어?
```
### OUTPUT
- intent: `overload_check`
- detail: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- reasoning: 과부하 장비 확인 요청

---
## Step 2: InfoAgent (정보조회)
### INPUT
- intent: `overload_check`
- detail: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
### TOOL CALLS
- `get_overloaded_equipment({})`

---
## Step 2: InfoAgent (정보조회)
### INPUT
- intent: `overload_check`
- detail: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`

---
## Step 3: ResponseAgent (응답생성)
### OUTPUT
```
1시간 내 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 부하율(%) | 상태    |
| ------------- | --------- | ---- | ------ | -------- | ------- |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 99.8     | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 99.3     | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 99.2     | ERROR   |
| SHT-L3-MODULE-01| SHUTTLE   | L3   | MODULE | 99.2     | ERROR   |
| AGV-L1-CELL-01 | AGV       | L1   | CELL   | 99.1     | ERROR   |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 98.3     | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 98.1     | ERROR   |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 96.9     | ERROR   |
| SHT-L1-TFT-01  | SHUTTLE   | L1   | TFT    | 95.6     | ERROR   |
| CRN-L1-MODULE-01| CRANE     | L1   | MODULE | 95.6     | ERROR   |
| SHT-L1-TFT-01  | SHUTTLE   | L1   | TFT    | 95.3     | ERROR   |
| SHT-L1-TFT-02  | SHUTTLE   | L1   | TFT    | 95.3     | ERROR   |
| SHT-L1-TFT-02  | SHUTTLE   | L1   | TFT    | 95.0     | ERROR   |
| SHT-L3-MODULE-01| SHUTTLE   | L3   | MODULE | 94.8     | ERROR   |
| AGV-L1-CELL-01 | AGV       | L1   | CELL   | 94.7     | ERROR   |
| SHT-L1-TFT-02  | SHUTTLE   | L1   | TFT    | 94.0     | ERROR   |
| AGV-L1-CELL-01 | AGV       | L1   | CELL   | 93.0     | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 93.0     | ERROR   |
| SHT-L1-TFT-01  | SHUTTLE   | L1   | TFT    | 92.9     | ERROR   |
| SHT-L1-TFT-02  | SHUTTLE   | L1   | TFT    | 92.7     | ERROR   |
| AGV-L1-CELL-01 | AGV       | L1   | CELL   | 92.1     | ERROR   |
| SHT-L3-TFT-02  | SHUTTLE   | L3   | TFT    | 91.6     | ERROR   |
| CRN-L1-MODULE-01| CRANE     | L1   | MODULE | 91.2     | ERROR   |
| CRN-L1-MODULE-01| CRANE     | L1   | MODULE | 91.2     | ERROR   |
| SHT-L3-MODULE-01| SHUTTLE   | L3   | MODULE | 91.2     | ERROR   |
| CRN-L1-MODULE-01| CRANE     | L1   | MODULE | 90.7     | ERROR   |
| SHT-L3-MODULE-01| SHUTTLE   | L3   | MODULE | 90.5     | ERROR   |
| SHT-L3-TFT-02  | SHUTTLE   | L3   | TFT    | 90.5     | ERROR   |
| SHT-L3-TFT-02  | SHUTTLE   | L3   | TFT    | 90.4     | ERROR   |
| SHT-L3-TFT-02  | SHUTTLE   | L3   | TFT    | 90.1     | ERROR   |
| SHT-L3-TFT-02  | SHUTTLE   | L3   | TFT    | 89.4     | ERROR   |
| SHT-L1-TFT-02  | SHUTTLE   | L1   | TFT    | 88.8     | ERROR   |
| CRN-L1-MODULE-01| CRANE     | L1   | MODULE | 88.8     | ERROR   |
| SHT-L1-TFT-01  | SHUTTLE   | L1   | TFT    | 88.5     | ERROR   |
| SHT-L1-TFT-01  | SHUTTLE   | L1   | TFT    | 87.9     | ERROR   |
| SHT-L3-MODULE-01| SHUTTLE   | L3   | MODULE | 87.8     | ERROR   |
| SHT-L3-TFT-02  | SHUTTLE   | L3   | TFT    | 87.1     | ERROR   |
| SHT-L3-MODULE-01| SHUTTLE   | L3   | MODULE | 86.6     | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 86.4     | ERROR   |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 86.3     | ERROR   |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 86.1     | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 85.6     | ERROR   |
| SHT-L1-TFT-02  | SHUTTLE   | L1   | TFT    | 85.4     | ERROR   |
| AGV-L1-CELL-01 | AGV       | L1   | CELL   | 85.1     | ERROR   |
| STK-L1-PACK-01 | STACKER   | L1   | PACK   | 84.8     | RUNNING |
| CRN-L2-MODULE-01| CRANE     | L2   | MODULE | 84.8     | RUNNING |
| AGV-L1-CELL-01 | AGV       | L1   | CELL   | 84.6     | ERROR   |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 84.6     | ERROR   |
| SHT-L1-TFT-01  | SHUTTLE   | L1   | TFT    | 84.5     | ERROR   |
| CRN-L1-MODULE-01| CRANE     | L1   | MODULE | 84.3     | ERROR   |
| SRT-L3-PACK-01 | SORTER    | L3   | PACK   | 84.0     | RUNNING |
| STK-L1-PACK-01 | STACKER   | L1   | PACK   | 83.1     | RUNNING |
| CVR-L1-TFT-02  | CONVEYOR  | L1   | TFT    | 82.9     | RUNNING |
| CVR-L1-PACK-01 | CONVEYOR  | L1   | PACK   | 82.1     | RUNNING |
| CRN-L2-MODULE-01| CRANE     | L2   | MODULE | 81.6     | RUNNING |
| CRN-L1-CELL-01 | CRANE     | L1   | CELL   | 79.6     | RUNNING |
| CRN-L1-CELL-01 | CRANE     | L1   | CELL   | 79.2     | RUNNING |
| SHT-L3-PACK-01 | SHUTTLE   | L3   | PACK   | 78.6     | RUNNING |
| CRN-L1-CELL-01 | CRANE     | L1   | CELL   | 73.1     | RUNNING |
| CRN-L1-CELL-01 | CRANE     | L1   | CELL   | 71.0     | RUNNING |
```