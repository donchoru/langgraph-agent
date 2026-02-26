# Agent Trace Log
- **시간**: 2026-02-26 14:57:15
- **사용자 입력**: 과부하 장비 있어?
- **최종 의도**: overload_check

---
## Step 1: IntentAgent (의도분석)
### State BEFORE
### State Snapshot
- **user_input**: `과부하 장비 있어?`
- **intent**: ``
- **intent_detail**: ``
- **final_answer**: ``
- **messages** (0건):
### LLM 호출
- input: `과부하 장비 있어?`
### LLM 출력
- intent: `overload_check`
- detail: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- reasoning: 과부하 장비 확인 요청
### State AFTER
### State Snapshot
- **user_input**: `과부하 장비 있어?`
- **intent**: `overload_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (0건):

---
## Step 2: InfoAgent (정보조회)
### State BEFORE
### State Snapshot
- **user_input**: `과부하 장비 있어?`
- **intent**: `overload_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (0건):
### LLM 호출 (첫 호출)
### LLM 출력 → Tool 호출 요청
- `get_overloaded_equipment({})`
### 다음: ToolNode로 이동
### State AFTER
### State Snapshot
- **user_input**: `과부하 장비 있어?`
- **intent**: `overload_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (1건):
  - **AIMessage** [tool_calls]: `get_overloaded_equipment({})`

---
## Step 2.5: ToolNode (SQL 실행)
### State BEFORE
### State Snapshot
- **user_input**: `과부하 장비 있어?`
- **intent**: `overload_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (1건):
  - **AIMessage** [tool_calls]: `get_overloaded_equipment({})`
### 실행할 Tool
- `get_overloaded_equipment({})`
### Tool 실행 결과
- **ToolMessage** (tool=`get_overloaded_equipment`):
  ```
  [{"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "status": "ERROR", "recorded_at": "2026-02-26 14:17:01", "load_rate_pct": 99.8, "warning_pct": 80.0, "critical_pct": 95.0}, {"equipment_id": "SHT-L3-CELL-01", "equipment_type": "SHUTTLE", "line": "L3", "zone": "CELL", "status": "ERROR", "recorded_at": "2026-02-26 14:07:01", "load_rate_pct": 99.3, "warning_pct": 78.0, "critical_pct": 92.0}, {"equipment_id": "SHT-L3-CELL-01", "equipment_type": "SHUTTLE"...
  ```
### State AFTER
### State Snapshot
- **user_input**: `과부하 장비 있어?`
- **intent**: `overload_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (2건):
  - **AIMessage** [tool_calls]: `get_overloaded_equipment({})`
  - **ToolMessage** (tool=`get_overloaded_equipment`): `[{"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "status": "ERROR", "recorded_at": "2026-02-26 14:17:01", "load_rate_pct": 99.8, "warning_pct": 80.0, "critical_pct": 95.0}, {"equipment_id": "SHT-L3-CELL-01", "equipment_type": "SHUTTLE", "line": "L3", "z...`

---
## Step 2: InfoAgent 재진입 (Tool 결과 수신)
### State BEFORE
### State Snapshot
- **user_input**: `과부하 장비 있어?`
- **intent**: `overload_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (2건):
  - **AIMessage** [tool_calls]: `get_overloaded_equipment({})`
  - **ToolMessage** (tool=`get_overloaded_equipment`): `[{"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "status": "ERROR", "recorded_at": "2026-02-26 14:17:01", "load_rate_pct": 99.8, "warning_pct": 80.0, "critical_pct": 95.0}, {"equipment_id": "SHT-L3-CELL-01", "equipment_type": "SHUTTLE", "line": "L3", "z...`
### LLM 호출 (메시지 히스토리 2건 포함)
### LLM 출력 → 텍스트 응답
```
1시간 내 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 부하율 (%) | 상태    |
| :------------- | :-------- | :--- | :----- | :--------- | :------ |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 99.8       | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 99.3       | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 99.2       | ERROR   |
| SHT-L3-MODULE-01| SHUTTLE   | L3   | MODULE | 99.2       | ERROR   |
| AGV-L1-CELL-01 | AGV       | L1   | CELL   | 99.1       | ERROR  
```
### 다음: ResponseAgent로 이동
### State AFTER
### State Snapshot
- **user_input**: `과부하 장비 있어?`
- **intent**: `overload_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (3건):
  - **AIMessage** [tool_calls]: `get_overloaded_equipment({})`
  - **ToolMessage** (tool=`get_overloaded_equipment`): `[{"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "status": "ERROR", "recorded_at": "2026-02-26 14:17:01", "load_rate_pct": 99.8, "warning_pct": 80.0, "critical_pct": 95.0}, {"equipment_id": "SHT-L3-CELL-01", "equipment_type": "SHUTTLE", "line": "L3", "z...`
  - **AIMessage**: 1시간 내 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 부하율 (%) | 상태    |
| :------------- | :-------- | :--- | :----- | :--------- | :------ |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 99.8       | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 99.3       | ERROR   |
| SHT-L3...

---
## Step 3: ResponseAgent (응답생성)
### State BEFORE
### State Snapshot
- **user_input**: `과부하 장비 있어?`
- **intent**: `overload_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (3건):
  - **AIMessage** [tool_calls]: `get_overloaded_equipment({})`
  - **ToolMessage** (tool=`get_overloaded_equipment`): `[{"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "status": "ERROR", "recorded_at": "2026-02-26 14:17:01", "load_rate_pct": 99.8, "warning_pct": 80.0, "critical_pct": 95.0}, {"equipment_id": "SHT-L3-CELL-01", "equipment_type": "SHUTTLE", "line": "L3", "z...`
  - **AIMessage**: 1시간 내 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 부하율 (%) | 상태    |
| :------------- | :-------- | :--- | :----- | :--------- | :------ |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 99.8       | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 99.3       | ERROR   |
| SHT-L3...
### 처리: 메시지 히스토리에서 최종 AI 응답 추출
### 최종 응답 (final_answer)
```
1시간 내 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 부하율 (%) | 상태    |
| :------------- | :-------- | :--- | :----- | :--------- | :------ |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 99.8       | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 99.3       | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 99.2       | ERROR   |
| SHT-L3-MODULE-01| SHUTTLE   | L3   | MODULE | 99.2       | ERROR   |
| AGV-L1-CELL-01 | AGV       | L1   | CELL   | 99.1       | ERROR   |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 98.3       | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 98.1       | ERROR   |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 96.9       | ERROR   |
| SHT-L1-TFT-01  | SHUTTLE   | L1   | TFT    | 95.6       | ERROR   |
| CRN-L1-MODULE-01| CRANE     | L1   | MODULE | 95.6       | ERROR   |
| SHT-L1-TFT-01  | SHUTTLE   | L1   | TFT    | 95.3       | ERROR   |
| SHT-L1-TFT-02  | SHUTTLE   | L1   | TFT    | 95.3       | ERROR   |
| SHT-L1-TFT-02  | SHUTTLE   | L1   | TFT    | 95.0       | ERROR   |
| SHT-L3-MODULE-01| SHUTTLE   | L3   | MODULE | 94.8       | ERROR   |
| AGV-L1-CELL-01 | AGV       | L1   | CELL   | 94.7       | ERROR   |
| SHT-L1-TFT-02  | SHUTTLE   | L1   | TFT    | 94.0       | ERROR   |
| AGV-L1-CELL-01 | AGV       | L1   | CELL   | 93.0       | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 93.0       | ERROR   |
| SHT-L1-TFT-01  | SHUTTLE   | L1   | TFT    | 92.9       | ERROR   |
| SHT-L1-TFT-02  | SHUTTLE   | L1   | TFT    | 92.7       | ERROR   |
| AGV-L1-CELL-01 | AGV       | L1   | CELL   | 92.1       | ERROR   |
| SHT-L3-TFT-02  | SHUTTLE   | L3   | TFT    | 91.6       | ERROR   |
| CRN-L1-MODULE-01| CRANE     | L1   | MODULE | 91.2       | ERROR   |
| CRN-L1-MODULE-01| CRANE     | L1   | MODULE | 91.2       | ERROR   |
| SHT-L3-MODULE-01| SHUTTLE   | L3   | MODULE | 91.2       | ERROR   |
| CRN-L1-MODULE-01| CRANE     | L1   | MODULE | 90.7       | ERROR   |
| SHT-L3-MODULE-01| SHUTTLE   | L3   | MODULE | 90.5       | ERROR   |
| SHT-L3-TFT-02  | SHUTTLE   | L3   | TFT    | 90.5       | ERROR   |
| SHT-L3-TFT-02  | SHUTTLE   | L3   | TFT    | 90.4       | ERROR   |
| SHT-L3-TFT-02  | SHUTTLE   | L3   | TFT    | 90.1       | ERROR   |
| SHT-L3-TFT-02  | SHUTTLE   | L3   | TFT    | 89.4       | ERROR   |
| SHT-L1-TFT-02  | SHUTTLE   | L1   | TFT    | 88.8       | ERROR   |
| CRN-L1-MODULE-01| CRANE     | L1   | MODULE | 88.8       | ERROR   |
| SHT-L1-TFT-01  | SHUTTLE   | L1   | TFT    | 88.5       | ERROR   |
| SHT-L1-TFT-01  | SHUTTLE   | L1   | TFT    | 87.9       | ERROR   |
| SHT-L3-MODULE-01| SHUTTLE   | L3   | MODULE | 87.8       | ERROR   |
| SHT-L3-TFT-02  | SHUTTLE   | L3   | TFT    | 87.1       | ERROR   |
| SHT-L3-MODULE-01| SHUTTLE   | L3   | MODULE | 86.6       | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 86.4       | ERROR   |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 86.3       | ERROR   |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 86.1       | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 85.6       | ERROR   |
| SHT-L1-TFT-02  | SHUTTLE   | L1   | TFT    | 85.4       | ERROR   |
| AGV-L1-CELL-01 | AGV       | L1   | CELL   | 85.1       | ERROR   |
| STK-L1-PACK-01 | STACKER   | L1   | PACK   | 84.8       | RUNNING |
| CRN-L2-MODULE-01| CRANE     | L2   | MODULE | 84.8       | RUNNING |
| AGV-L1-CELL-01 | AGV       | L1   | CELL   | 84.6       | ERROR   |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 84.6       | ERROR   |
| SHT-L1-TFT-01  | SHUTTLE   | L1   | TFT    | 84.5       | ERROR   |
| CRN-L1-MODULE-01| CRANE     | L1   | MODULE | 84.3       | ERROR   |
| SRT-L3-PACK-01 | SORTER    | L3   | PACK   | 84.0       | RUNNING |
| STK-L1-PACK-01 | STACKER   | L1   | PACK   | 83.1       | RUNNING |
| CVR-L1-TFT-02  | CONVEYOR  | L1   | TFT    | 82.9       | RUNNING |
| CVR-L1-PACK-01 | CONVEYOR  | L1   | PACK   | 82.1       | RUNNING |
| CRN-L2-MODULE-01| CRANE     | L2   | MODULE | 81.6       | RUNNING |
| CRN-L1-CELL-01 | CRANE     | L1   | CELL   | 79.6       | RUNNING |
| CRN-L1-CELL-01 | CRANE     | L1   | CELL   | 79.2       | RUNNING |
| SHT-L3-PACK-01 | SHUTTLE   | L3   | PACK   | 78.6       | RUNNING |
| CRN-L1-CELL-01 | CRANE     | L1   | CELL   | 73.1       | RUNNING |
| CRN-L1-CELL-01 | CRANE     | L1   | CELL   | 71.0       | RUNNING |
```
### State AFTER
### State Snapshot
- **user_input**: `과부하 장비 있어?`
- **intent**: `overload_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: `1시간 내 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 부하율 (%) | 상태    |
| :------------- | :-------- | :--- | :----- | :--------- | :------ |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 9`
- **messages** (3건):
  - **AIMessage** [tool_calls]: `get_overloaded_equipment({})`
  - **ToolMessage** (tool=`get_overloaded_equipment`): `[{"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "status": "ERROR", "recorded_at": "2026-02-26 14:17:01", "load_rate_pct": 99.8, "warning_pct": 80.0, "critical_pct": 95.0}, {"equipment_id": "SHT-L3-CELL-01", "equipment_type": "SHUTTLE", "line": "L3", "z...`
  - **AIMessage**: 1시간 내 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 부하율 (%) | 상태    |
| :------------- | :-------- | :--- | :----- | :--------- | :------ |
| CVR-L1-CELL-01 | CONVEYOR  | L1   | CELL   | 99.8       | ERROR   |
| SHT-L3-CELL-01 | SHUTTLE   | L3   | CELL   | 99.3       | ERROR   |
| SHT-L3...